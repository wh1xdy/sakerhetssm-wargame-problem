# How to solve VoiceOfNature

## Method 1: Guessing

As MrStalker knows the interests of people, and we have the name of the person, we could construct a search query and then look through each answer.

```
elin photography blogging
```

The flag is can be found on the correct Elin's page.

## Method 2: Git history

We know that the website is hosted at `https://voiceofnature.github.io`. It is likely that `voiceofnature` is the GitHub username. https://github.com/voiceofnature reveals that there is one public repository - voiceofnature.github.io.

In the commit history we can see that certain commits lacks a profile picture - perhaps there is something going on with these commits?

By either cloning the repo locally and using `git log`, or by looking through the commits individually and appending `.patch` to the URL, we can see that a specific commit uses an e-mail address on the format `name.lastname.year@domain.tld`. The URL for this commit is https://github.com/VoiceOfNature/VoiceOfNature.github.io/commit/91b79f113d1e03bd74d7a0febea2455b58c759d0.patch.

```git-log
commit 91b79f113d1e03bd74d7a0febea2455b58c759d0
Author: VoiceOfNature <elin.andersson.96@penguinmail.com>
Date:   Fri Mar 18 19:02:11 2022 +0000

    Add photos from my phone

    Having a terminal app on my phone is so convenient!
```

Searching for `Elin Andersson 1996` gives us just one Elin Andersson born in 1996. The flag can be found on the correct Elin's page.

/person?personalnumber=960814-2284
