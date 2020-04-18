New in `1.30`:

| Ability to ignore tests.
| Run summary for all tests at the end.

New in `1.29`:

| Added `finally` code block. Now you can specify cleanup steps.

New in `1.28`:

| Added `sh` step.
| Added `astuple`, `asint`, `asfloat`, `aslist`, `asdict`, `asstr` type conversion filters.

New in `1.27`:

| Added `skip_if` condition. Now you can skip steps based on checks condition.

New in `1.26`:

| Added `asdate` and `astimestamp` date filters.
| Added `now`, `now_ts`, `astimestamp`, `asdate` filters and functions.
| Filters refactoring - now built in filters use the same load logic, as custom.

New in `1.25`:

| Added custom filters support via `-f` parameter.

New in `1.24`:

| Added colorful output.
| Added idents for included tests output.

New in `1.23`:

| Reports are now longer created in `./`. Dedicated `./reports` directory is used instead.

New in `1.22`:

| Hash filters.

New in `1.20`:

| Save output to file as json, including step definitions and variables before and after. Useful for debugging.
| `catcher -p json test.yml`

New in `1.19`:

| To have `docker-compose` support install `catcher[compose]` instead.
| This will make catcher run `docker-compose up` in your resources directory, if docker-compose file was found.
