# Story lifecycle

Read Ideal/spec/state/graph and the active story before implementation.
`Draft` means missing design/substrate evidence; `Pending` means buildable now;
`In Progress` means underway; `Blocked` needs a concrete blocker and reopen
condition; `Done` needs validation and closure. Edit story files and state,
then run `make methodology-compile`; never edit the generated story index.

Use `/create-story`, `/build-story`, `/validate`, `/mark-story-done`.
Local commands and VLC UI acceptance criteria govern imported examples.
Any user-facing slice includes its actual macOS timeline interactions and UI
verification. Plan approval respects existing user authorization.
