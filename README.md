# Webhooks

This serves as a central place to receive webhooks, store the data and process the data.

The pattern here prioritises storing the data in the webhook and returning a success to the calling third party. Processing that data is then done asyncronously.

Why:

1. We can fix bugs and re-process data on our own schedule without exposing failures to the third party. Shopify's retry logic is to try a few times and then disable the webhook; not sending messages that would otherwise be processed successfully.

2. We can control the load using a queue. When we launch new popular products we receive a lot of webhooks. This has taken Sylius down. Instead, the queue length will grow and we can deal with that how we want.

3. We can route processing beyond Sylius. Multiple subscribers can act on the message bus; allowing us to retain the existing Sylius behaviour while adding non-Sylius destinations for the data.

### How it works

We will run through the Shopify web hook as an example, but future additions should use a similar pattern

![Architecture Diagram](https://github.com/Cubitts-KX/webhooks/blob/main/aws_diagram.svg?raw=true)

##### Storing the data sent by the third party

1. We have an API route for /service/resource/action; in the case of Shopify - /shopify/order/create and configure the service to post data there.

2. We have a data storing lambda which stores the data in S3. This also creates the key for the data, so we store the data using the Shopify Order ID at s3://bucket-name/shopify/order/create/shopify_order_id.json making it easier for us to find an order's data in the bucket.

3. The bucket is configured to emit an event to the default eventbridge bus on object creation.

4. We then return a 201 success code with no body to the calling service.

##### Processing the data

5. We have an Eventbridge rule that filters for events in the shopify/order/create path within the bucket and sends that event to a queue

6. The queue stores filtered events and allows a lambda to consume from it. It is also configured to use a dead letter queue after retrying.

7. The data processing lambda parses the event to get the bucket and object details and downloads the stored JSON from the bucket. Then it sends that data to the legacy webhook endpoint in Sylius. If there are any problems, or the Sylius endpoint returns an unsuccessful response we raise an exception.

8. Any exceptions will result in the lambda retrying 3 times before it lands in the dead letter queue. After investigating and fixing the issue, the messages in the DLQ can be sent back to the original queue for reprocessing.

### Retrying

Messages will be sent to the DLQ after being retried 3 times.

Message will remain in the DLQ for up to 14 days.

Log into the AWS console, navigate to the DLQ and press the "redrive" button to send the messages back to the original queue for them to be reprocessed.
