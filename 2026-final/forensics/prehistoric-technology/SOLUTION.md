# SOLUTION
1. Analyze the environment and observe that communication uses NetBIOS and the login flow relies on LM authentication. Extract the challenge values.
2. Format the values according to your password cracking tool of choice. For `john`, it can look like the following:
`UFFEK::REGERINGEN:4457c3bb000b6aa098e5b548d8d5c088f60e291a17db1dca:000000000000000000000000000000000000000000000000:54fa55d1b4b7cd22`
3. The exact cracking approach depends on the tool being used. When using `john`, begin by cracking the first half of the password with the `nethalflm` format and a mask of seven uppercase characters. For example: `john --format=nethalflm --mask='?u?u?u?u?u?u?u' hash`.
4. Once the first half of the password is recovered, run `john` again using the full `netlm` format and include the recovered half in the mask: `john --format=netlm --mask='SSTANRE?u?u?u?u?u?u?u' hash`
