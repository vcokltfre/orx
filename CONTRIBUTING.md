# Contributing to Orx

Thank you for your interest in contributing to Orx!

There are a few important rules which must be followed when contributing to the library:

1. Unless you are fixing a small bug/typo/similar, always open an issue and wait for it to be assigned to you before you create a pull request.
2. Follow the commit conventions laid out below.
3. Lint before you PR. You can run the project's chosen linter settings by using `poetry run task lint`.

## Commit Conventions

All commits should be created using the following format:

`type(scope): body`

If no major scope fits, the scope can be excluded from the message.

Example of commit messages formatted this way:

- `feat(core): add create_guild_channel method to HTTPClient`
- `fix(core): fix ratelimit handling in HTTPClient (#1234)`
- `chore(core): add support for custom HTTP headers in HTTPClient request()`
- `docs(core): add documentation for HTTPClient.request()`

For more information see [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

The valid commit types for this project are:

- feat
- fix
- chore
- docs
