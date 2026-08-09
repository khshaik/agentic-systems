# Prompts to verify `.goosehints`

Start Goose from the repository root in a new session before using these.

## 1. Root context loaded at session start

```text
Before changing anything, summarize this project's purpose, canonical verification command, money representation, collaboration preferences, and definition of done. Cite the project files that establish each answer.
```

Expected evidence includes the root `.goosehints` and `docs/domain-rules.md` loaded through its `@` reference.

## 2. Use the context on a real task

```text
Add support for a 5% discount example to the CLI documentation. Follow all project instructions, make the smallest change, run the required verification, and report evidence.
```

## 3. Trigger package-specific nested hints

```text
Inspect src/order_service/service.py. Explain the package-specific rules that apply before proposing any change. Do not edit files.
```

## 4. Trigger the most-specific API hints

```text
Review src/order_service/api/handlers.py for contract and validation risks. State all applicable repository, package, and API-directory conventions. Do not edit files.
```

## 5. Trigger test-specific hints

```text
Add a boundary test for the maximum allowed discount. Follow the test-directory conventions and run the required checks.
```

## 6. Demonstrate restart behavior

Edit a harmless preference in the root `.goosehints`, then ask about it in the current session and in a newly started session. The official documentation instructs users to restart the session after updating hints so the change is read at startup.
