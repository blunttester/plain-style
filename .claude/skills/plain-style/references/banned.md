<!-- plain-style: allow-file=banned-word,long-sentence,glossary-synonym reason: this file lists the banned words, so every row would self-report -->

# Banned words and phrases

`scripts/check_docs.py` reads the tables in this file. Keep the two-column
format: the first cell is the word or pattern, the second is the replacement.
`delete` in the second column means cut the word and change nothing else.

A term in the first cell may be a plain phrase or a regular expression wrapped
in slashes, for example `/\bin order to\b/`. Use the regular expression form
when a word is filler in one context and correct in another: `just` is filler in
"just run the script" and correct in "just the header row".

To add a word, add a row. To stop flagging a word, remove the row. There is no
second list inside the script.

## Inflated verbs and nouns

| Word or pattern | Use instead |
|-----------------|-------------|
| leverage | use |
| utilize | use |
| utilise | use |
| ensure | make sure, check that, confirm that |
| robust | delete, or say what it survives |
| streamline | simplify, shorten |
| seamless | delete |
| seamlessly | delete |
| comprehensive | complete, or say what it covers |
| facilitate | help, let |
| initiate | start |
| terminate | stop, end |
| commence | start |
| endeavour | try |
| methodology | method |
| functionality | features, or name the feature |
| capabilities | features, or name the feature |
| architected | designed, built |
| operationalize | put into use |
| orchestrate | coordinate, or name the orchestrator |
| holistic | delete |
| paradigm | delete |
| synergy | delete |
| ecosystem | delete, or name the tools |
| preamble | delete |

## LLM tells

| Word or pattern | Use instead |
|-----------------|-------------|
| delve into | look at, examine |
| dive into | look at, examine |
| underscore | show, prove |
| showcase | show |
| myriad | many |
| plethora | many |
| crucial | important, or say what breaks |
| vital | important, or say what breaks |
| pivotal | important, or say what breaks |
| significantly | delete, or give the number |
| dramatically | delete, or give the number |
| furthermore | delete |
| moreover | delete |
| additionally | also, or delete |
| in the realm of | in |
| when it comes to | for, in |
| it is important to note that | delete |
| it should be noted that | delete |
| note that | delete |
| please note | delete |
| as we can see | delete |
| in this section we will | delete |
| in this document | delete |
| this guide will walk you through | delete |
| let's | delete, use the imperative |
| testament to | delete |
| game-changer | delete |
| cutting-edge | delete |
| state-of-the-art | delete |
| best-in-class | delete |
| unlock | delete, or say what it enables |
| empower | let, allow |
| elevate | improve |
| navigate the complexities | handle |
| at the end of the day | delete |
| rich tapestry | delete |

## Padding

| Word or pattern | Use instead |
|-----------------|-------------|
| in order to | to |
| in order for | for |
| due to the fact that | because |
| for the purpose of | to |
| with the exception of | except |
| in the event that | if |
| at this point in time | now |
| prior to | before |
| subsequent to | after |
| a number of | some, or give the number |
| the vast majority of | most |
| various different | several |
| each and every | every |
| first and foremost | first |
| basically | delete |
| essentially | delete |
| actually | delete |
| simply | delete |
| /\bjust\s+(?=run\b\|add\b\|use\b\|call\b\|do\b\|set\b\|click\b\|type\b\|open\b\|edit\b\|need\b\|needs\b\|have to\b\|has to\b\|want\b)/ | delete |
| very | delete |
| quite | delete |
| really | delete |
| in general | delete |
| generally speaking | delete |
| as a general rule | delete |
| type of | delete |
| kind of | delete |

## Hedging

Hedge only where the uncertainty is real. Then say what is uncertain and why,
instead of softening the sentence.

| Word or pattern | Use instead |
|-----------------|-------------|
| it seems that | delete |
| it appears that | delete |
| arguably | delete |
| somewhat | delete |
| fairly | delete |
| relatively | delete, or give the comparison |
| may potentially | may |
| could potentially | could |
| should probably | should |
| tends to | delete |
| in most cases | say which cases |

## Condescension

| Word or pattern | Use instead |
|-----------------|-------------|
| obviously | delete |
| /\bclearly\s+(?!label\|labell?ed\|mark\|marked\|separat\|document\|documented\|visible\|defined\|named)/ | delete |
| of course | delete |
| as you know | delete |
| needless to say | delete |
| trivially | delete |
| /\b(?:is\|it'?s\|very\|really\|quite\|pretty\|so)\s+easy\b\|\beasy\s+to\b/ | delete, or say how long it takes |
| easily | delete |
| straightforward | delete |
| sanity check | check, validation |

## Words that survive

These look like filler and are not. Keep them where they carry the meaning:
idempotent, deterministic, atomic, source of truth, breaking change,
backwards compatible, eventually consistent.
