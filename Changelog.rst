New in `1.23.0`:

| Reports are now longer created in `./`. Dedicated `./reports` directory is used instead.

New in `1.22.0`:

| Hash filters.

New in `1.20.0`:

| Save output to file as json, including step definitions and variables before and after. Useful for debugging.
| `catcher -p json test.yml`

New in `1.19.0`:

| To have `docker-compose` support install `catcher[compose]` instead.
| This will make catcher run `docker-compose up` in your resources directory, if docker-compose file was found.
