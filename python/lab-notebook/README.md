# Lab Notebook Probe

Exercises the Lab-kernel facade used by notebook-style immediate execution.
Outside a Mercurio Lab kernel the script exits successfully with a skip message;
inside Lab it opens the active workspace, forks a small parameter sweep, and
checks semantic helper delegation when a workspace is available.

Run from the repository root:

```powershell
python mercurio-examples/python/lab-notebook/probe_lab_kernel.py
```

To force Lab mode for local smoke testing, set `MERCURIO_LAB_KERNEL=1` and
`MERCURIO_WORKSPACE` to a descriptor-backed example project.
