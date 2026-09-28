<!-- plain-style: allow-file=banned-word reason: quotes the original rules and shows bad examples -->

# Orwell's six rules, applied to documentation

From *Politics and the English Language*, 1946. Orwell wrote about political
prose, but the failure mode is the same one documentation has: words arriving
by habit instead of by choice. Each rule below has the original wording, the
reason it matters here, and a pair from real docs.

## 1. Never use a metaphor, simile, or figure of speech which you are used to seeing in print

A dead metaphor asks the reader to decode an image that carries no meaning. The
reader pays the cost and gets nothing.

> Before: The cache is the beating heart of the service, and the importer is
> where the rubber meets the road.

> After: The cache holds each response for 60 seconds. The importer reads a CSV
> row and writes it to the `orders` table.

Common offenders in software docs: under the hood, out of the box, first-class
citizen, low-hanging fruit, moving parts, heavy lifting, plug and play. Keep
"source of truth"; it has a precise meaning.

## 2. Never use a long word where a short one will do

Long words are not more precise. They are usually less precise, because the
writer reached for register instead of meaning.

> Before: Utilize the configuration file to facilitate initialization of the
> environment.

> After: Use the config file to start the environment.

`references/banned.md` holds the list.

## 3. If it is possible to cut a word out, always cut it out

Apply this to whole paragraphs first. Most drafts have two paragraphs to cut.
The first says what the document will cover. The last says what it covered.

> Before: In this section, we will take a look at the various different options
> that are available to you in order to configure the importer.

> After: You can configure the importer in three ways:

## 4. Never use the passive where you can use the active

Passive voice drops the actor. In documentation the actor is usually the fact
the reader needs: who runs this, what breaks it, which process owns the file.

> Before: The temporary directory is populated and the log file is updated.

> After: The importer writes each row to `tmp/` and appends a line to
> `import.log`.

Passive is right when the actor is unknown or beside the point. "The record was
deleted last year" is fine when nobody knows who deleted it.

## 5. Never use a foreign phrase, a scientific word, or a jargon word if you can think of an everyday English equivalent

Jargon the reader shares is efficient; jargon the reader does not share is a
lock on the door. Judge by the reader in `references/doc-types.md`, not by the
writer's comfort.

Keep: idempotent, commit, container, schema. These have exact meanings and the
reader knows them.

Drop: leverage, orchestrate (unless you mean an orchestrator), paradigm,
methodology, de facto, per se, i.e. when you mean "that is".

> Before: Per se, the import step is idempotent vis-à-vis the source state.

> After: Importing the same file twice produces the same rows.

## 6. Break any of these rules sooner than say anything outright barbarous

This rule outranks the other five, and it outranks the checker. If following a
rule produces a sentence that is awkward, wrong, or unsafe, keep the good
sentence. Record the reason:

```markdown
<!-- plain-style: allow=long-sentence reason: splitting this warning separates the condition from the action -->
```

The rule protects judgement. It does not protect a draft you did not revise. If
a file needs more than two or three waivers, step 3 of the workflow was skipped.

## Using the rules as a tiebreaker

STE says use a shorter sentence. Google says use second person. When two rules
point in different directions, ask Orwell's real question: which version makes
the reader work less? Then write that one.
