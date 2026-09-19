# Subagent Delegation Guidance

Use a subagent only when an independent task can reduce the total time. Do small tasks directly.

Give each subagent one clear task. State the input, the required result, and the stop condition.

Use `fork_turns: "none"` with a self-contained task when possible. Give recent turns only when the task needs them. Do not copy the full conversation by default.

Ask for the main finding or blocker as soon as it is known. Keep the final report short. Stop work that is no longer needed.

Keep one writer for a shared Rhino document. Give separate output paths to agents that make files.
