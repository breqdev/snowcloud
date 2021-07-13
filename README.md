# snowcloud

Snowcloud is a service for generating unique, time-ordered, 64-bit IDs across distributed worker processes. This format is commonly called "snowflake" IDs, and is used by [Twitter](https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake) and [Discord](https://discord.com/developers/docs/reference#snowflakes).

## Snowflake ID Format

| Timestamp | Worker ID | Increment |
| --------- | --------- | --------- |
| 42 bits   | 10 bits   | 12 bits   |
| milliseconds since Jan 1, 2020 | allocated by delegator | incremented by generator |

## Snowcloud Deployment Structure

A Snowcloud deployment consists of a *delegator* and many *generators*.

### Delegator

The delegator (located in `snowcloud/delegator.py`, run with e.g. `python3 -m snowcloud.delegator`) keeps track of assigning worker IDs to different generator processes. It uses [Redis](https://redis.io) to keep track of a pool of worker IDs. It then allows clients to register for a worker ID or renew their existing worker ID.

### Generators

Generators obtain a worker ID from the delegator and use it to generate their own Snowflake IDs. These can be integrated into Flask applications using the `snowcloud.flask_ext` module.

An example Flask server is located in `snowcloud/server.py`. However, more commonly, the Flask application would use the Snowflake ID internally instead. For instance, it could generate a Snowflake ID to use as the primary key column whenever it inserts a new row into the database.