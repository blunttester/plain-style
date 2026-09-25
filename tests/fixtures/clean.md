# Clean fixture

This file passes every rule. The tests use it to prove that a well-written
document exits zero.

The importer writes each row to `tmp/`. It then records the row ID in
`import.log`. A second run on the same input changes nothing.

## Steps

1. Set the context.
2. Check the queue depth.
3. If the queue is empty, stop the consumer.
