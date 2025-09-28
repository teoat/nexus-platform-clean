# [SSOT] <short description of anchor change>

## Summary

- **What changed**: <anchor id, files>
- **Why**: <reason for change>
- **Tests run**: <list of tests executed>
- **Rollback plan**: <snapshot path + commands>

## Changes Made

- [ ] Updated SSOT anchor: `<anchor_id>`
- [ ] Modified files: `<list of modified files>`
- [ ] Updated references: `<list of updated references>`
- [ ] Added validation: `<list of new validation rules>`

## SSOT Impact

- **Anchor Family**: `<family>`
- **Dependencies**: `<list of dependent anchors>`
- **Generated Files**: `<list of files generated from this anchor>`
- **Breaking Changes**: `<list of breaking changes, if any>`

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Contract tests pass
- [ ] Staging deployment successful
- [ ] No regression in functionality

## Validation

- [ ] `ssot-validate` passed
- [ ] `lockfile-check` passed
- [ ] `contract-test` passed
- [ ] `size-check` passed
- [ ] `lint-ssot` passed
- [ ] `security-scan` passed

## Approvals

- [ ] 2 approvals (CODEOWNERS)
- [ ] Platform team approval (if required)
- [ ] Security team approval (if security-related)

## Rollback Plan

If this PR causes issues, the following rollback steps should be taken:

1. **Immediate Rollback**:

   ```bash
   git revert <commit-hash>
   git push origin <branch-name>
   ```

2. **Restore from Snapshot**:

   ```bash
   # Restore from baseline snapshot
   tar -xzf snapshots/baseline-<timestamp>.tar.gz
   git checkout ssot-baseline-<timestamp>
   ```

3. **Service Restart** (if needed):
   ```bash
   # Restart affected services
   kubectl rollout restart deployment/<service-name>
   ```

## Monitoring

- [ ] Monitor system health after deployment
- [ ] Check SSOT sync status
- [ ] Verify generated files are correct
- [ ] Monitor for any errors or warnings

## Additional Notes

- <any additional context or notes>
- <links to related issues or discussions>
- <special considerations for this change>

---

**Template Version**: 1.0
**Last Updated**: 2025-01-27T12:30:00Z
