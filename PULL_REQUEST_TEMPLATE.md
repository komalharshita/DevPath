<!--
  Pull Request Template — DevPath
  --------------------------------
  Delete sections that do not apply.
  Every section marked [required] must be completed before review begins.
  PRs with empty required sections will be returned without review.
-->

## Summary [required]

<!-- One paragraph explaining what this PR does and why. -->
<!-- Do not just repeat the commit message or the issue title. -->



## Related Issue [required]

<!-- Every PR must link to an open issue. -->
<!-- If no issue exists, open one before submitting this PR. -->

Closes #

## Type of Change [required]

<!-- Check all that apply. -->

- [ ] Bug fix — resolves a broken behaviour
- [ ] Feature — adds new functionality
- [ ] Data — adds new projects to `data/projects.json`
- [ ] Documentation — updates docs, README, or code comments only
- [ ] Style — CSS or visual changes only, no logic change
- [ ] Refactor — restructures code without changing behaviour
- [ ] Test — adds or updates tests

## What Was Changed [required]

<!-- List every file you modified and briefly explain why. -->
<!-- Do not list files you only read. -->

| File | Change made |
|------|-------------|
| `utils/recommender.py` | Added `clear_cache()` function |
| `tests/test_basic.py` | Added test for cache invalidation |

## How to Test This PR [required]

<!-- Exact steps a reviewer can follow to verify your change works. -->
<!-- "It works on my machine" is not sufficient. -->

1. Clone this branch: `git checkout your-branch-name`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python src/app.py`
4. Open http://127.0.0.1:5000 and...
5. Run the tests: `python tests/test_basic.py`

Expected test output:
```
27 passed, 0 failed out of 27 tests
```

## Test Results [required]

<!-- Paste the full output of python tests/test_basic.py -->

```
paste output here
```

## Screenshots (if UI change)

<!-- Before and after screenshots for any visual change. -->
<!-- Remove this section if your PR has no visual change. -->

| Before | After |
|--------|-------|
| screenshot | screenshot |

## Self-Review Checklist [required]

<!-- Complete every item before requesting review. -->
<!-- Do not submit a PR you would not approve yourself. -->

- [ ] I have read [CONTRIBUTING.md](../CONTRIBUTING.md) and followed all guidelines
- [ ] My branch name follows the convention: `feat/`, `fix/`, `docs/`, `data/`, `style/`, `test/`
- [ ] I have run `python tests/test_basic.py` and all 27 tests pass
- [ ] I have run `flake8 .` locally and there are no errors
- [ ] I have not introduced any `print()` or `console.log()` debug statements
- [ ] Every new function I wrote has a docstring
- [ ] I have not modified files outside the scope of the linked issue
- [ ] If I changed the UI, I tested it at 375px (mobile) and 1280px (desktop)
- [ ] If I added a project to the dataset, it has all required JSON fields

## Notes for Reviewer

<!-- Anything you want the reviewer to pay particular attention to. -->
<!-- Or "None" if there is nothing unusual. -->


