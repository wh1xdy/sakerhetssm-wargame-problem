(() => {
    const root = document.querySelector("[data-girlypop-root]");
    if (!root) {
        return;
    }

    const els = {
        host: document.querySelector("[data-gp-host]"),
        distro: document.querySelector("[data-gp-distro]"),
        fileCount: document.querySelector("[data-gp-file-count]"),
        vibe: document.querySelector("[data-gp-vibe]"),
        status: document.querySelector("[data-gp-status]")
    };

    const setStatus = (text) => {
        if (els.status) {
            els.status.textContent = text;
        }
    };

    const getTextFromFileEndpoint = async (path) => {
        const res = await fetch(`/file?path=${encodeURIComponent(path)}`);
        if (!res.ok) {
            throw new Error(`Failed for ${path} (${res.status})`);
        }
        return await res.text();
    };

    const hash = (text) => {
        let h = 0;
        for (let i = 0; i < text.length; i += 1) {
            h = (h * 31 + text.charCodeAt(i)) >>> 0;
        }
        return h;
    };

    const hueToVibe = (hue) => {
        if (hue < 60) return "Cherry gloss";
        if (hue < 120) return "Peach fizz";
        if (hue < 180) return "Mint sparkle";
        if (hue < 240) return "Ocean shimmer";
        if (hue < 300) return "Lavender glow";
        return "Bubblegum pop";
    };

    const parseDistro = (osRelease) => {
        const nameMatch = osRelease.match(/^PRETTY_NAME=(.*)$/m);
        if (!nameMatch) {
            return "Unknown";
        }

        return nameMatch[1].replaceAll('"', "");
    };

    const updateUI = async () => {
        try {
            setStatus("Loading your sparkle profile...");

            const [hostnameRaw, osReleaseRaw, etcListingRaw] = await Promise.all([
                getTextFromFileEndpoint("/etc/hostname"),
                getTextFromFileEndpoint("/etc/os-release"),
                getTextFromFileEndpoint("/etc")
            ]);

            const hostname = hostnameRaw.trim() || "unknown-host";
            const distro = parseDistro(osReleaseRaw);
            const fileCount = etcListingRaw
                .split("\n")
                .map((line) => line.trim())
                .filter((line) => line.length > 0).length;

            const hue = hash(hostname) % 360;
            document.documentElement.style.setProperty("--gp-hue", String(hue));

            if (els.host) els.host.textContent = hostname;
            if (els.distro) els.distro.textContent = distro;
            if (els.fileCount) els.fileCount.textContent = `${fileCount} icons`;
            if (els.vibe) els.vibe.textContent = hueToVibe(hue);

            setStatus("Sparkle profile synced.");
        } catch (error) {
            setStatus("Sparkle profile unavailable. Sign in to unlock diagnostics.");
        }
    };

    void updateUI();
})();
