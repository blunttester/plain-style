# Dirty fixture

This file breaks rules on purpose, so do not clean it up. The tests read it to
prove that the checker exits 1 and reports what it found.

We leverage a robust pipeline in order to ensure seamless delivery, and the vast
majority of the various different edge cases are handled by a comprehensive set
of validators that the team has built over time for this exact purpose.

It is important to note that the temporary directory is populated — and the
log file is subsequently updated — by the import phase.
