<!-- plain-style: allow-file=banned-word,long-sentence,passive-voice,paragraph-length,em-dash reason: every "before" block is deliberately bad -->

# Before and after

Each pair covers one rule category. The "after" voice matches the target:
short, declarative, concrete, no hedging, facts in the order the reader needs
them.

## One term per concept

> **Before**
>
> The import job pulls rows from the source file. Each ingestion cycle writes
> to a temporary table. After the load completes, the transfer pass moves rows
> into `orders`.

> **After**
>
> An import job reads rows from the source file and writes them to a temporary
> table. The job then moves each row into `orders`.

Four names for one thing became one. The reader no longer wonders whether an
ingestion cycle and an import job differ.

## Sentence length

> **Before**
>
> If the deploy has failed and the pods are still in a CrashLoopBackOff state,
> you should roll back to the previous release, which can be found in the
> release history in the deployment tool, and then check the logs to see what
> the root cause was.

> **After**
>
> Check the pod state. If the pods are in `CrashLoopBackOff`, roll back to the
> previous release. Find that release in the deployment history. Then read the
> logs of the rolled-back pods.

## One instruction per step, condition before action

> **Before**
>
> 1. Stop the consumer and drain the queue, if the queue still has messages in
>    it, otherwise you can skip ahead to the verification step.

> **After**
>
> 1. Check the queue depth:
>
>    ```bash
>    rabbitmqctl list_queues name messages
>    ```
>
> 2. If the queue is empty, go to step 5.
> 3. Stop the consumer.
> 4. Drain the queue.

## Active voice

> **Before**
>
> The temporary directory is populated during the load phase and the log file
> is subsequently updated with the row identifiers that were processed.

> **After**
>
> The importer writes each row to `tmp/`, then records its ID in `import.log`.

## Plain words

> **Before**
>
> Leverage the configuration file to ensure the environment is initialised in a
> robust manner prior to commencing the import.

> **After**
>
> Use the config file to set up the environment before you import.

## No preamble, no summary

> **Before**
>
> ## Retiring content
>
> In this section, we will take a look at how content that is no longer
> relevant should be handled. It is important to note that there are several
> different approaches available. Let's dive in.
>
> Superseded documents are deleted rather than archived.
>
> In summary, we have seen that deletion is the preferred approach and that git
> history serves as the archive.

> **After**
>
> ## Retiring content
>
> Superseded documents are deleted, not archived. Git history is the archive:
>
> ```bash
> git log --diff-filter=D -- <path>     # find the commit that removed it
> git checkout <sha>^ -- <path>         # restore it
> ```
>
> There is no `archive/` directory. List every deletion in the pull request so
> a reviewer can object file by file.

## Warnings

> **Before**
>
> Run `make reset-db`. Note that data loss may be experienced if this is run
> against the production environment without taking the necessary precautions.

> **After**
>
> > **Warning: `make reset-db` deletes every row in `events`. There is no undo.
> > Check that `DATABASE_URL` points at staging before you run it.**
>
> ```bash
> echo "$DATABASE_URL"   # must contain "staging"
> make reset-db
> ```

## Prose for explanation, lists for parallel items

> **Before**
>
> - The classifier is LLM-backed
> - Deterministic output is not guaranteed
> - The validator exists
> - Human review is required

> **After**
>
> The classifier calls a model, so two runs on the same file can produce
> different labels. The validator rejects labels outside the allowed set, but
> it cannot spot a plausible wrong label. A human reviews every batch before
> release.

## Reasoning in a design doc

Short sentences and a real argument work together.

> **Before**
>
> Having carefully considered the various options that were available to us, it
> was ultimately decided that Postgres would be leveraged as the job store
> given its robust transactional guarantees and the comprehensive ecosystem of
> tooling that surrounds it.

> **After**
>
> We chose Postgres for the job store.
>
> The store needs transactions: a job updates its status and its result in one
> write, and a partial write leaves the job stuck. SQLite gives us transactions
> but one writer, and the importer runs four workers. DynamoDB scales further
> than we need and costs a migration. Postgres is already in the platform, so
> it adds no new operational surface.
>
> The cost is a network hop on every job update. At 1,200 jobs an hour that
> adds about 40 seconds, which we accept.

## Code comments

> **Before**
>
> ```python
> # Loop through the files and upload each one
> for path in paths:
>     upload(path)
> ```

> **After**
>
> ```python
> # Serial on purpose: the upload API rate-limits at 10 requests a second.
> for path in paths:
>     upload(path)
> ```

The first comment restates the code. The second says what the code cannot.
