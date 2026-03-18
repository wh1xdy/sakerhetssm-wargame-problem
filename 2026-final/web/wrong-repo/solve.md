# Solve

- Realize that the fork is deleted
- Realize that [commits in one fork are accessible from the forked repo](https://trufflesecurity.com/blog/anyone-can-access-deleted-and-private-repo-data-github)
- Access the hidden commit (enough of the hash is visible in the redacted screenshot) through the forked repo (https://github.com/forked-repo/commits/hidden-commits-hash)
- Find unredacted file

<details>
<summary>Spoiler</summary>
https://github.com/Kodsport/sakerhetssm-wargame-problem/commit/1ea9ba4
</details>

---

# Create
- Create fork
- Create path (`2026-final/web/wrong-repo`)
- Commit hidden file (`challenge.yml`)
- Push to GitHub (to other than `main` branch to minimize chance of accidental discovery)
- Take screenshot
- Delete fork repo (quickly)
