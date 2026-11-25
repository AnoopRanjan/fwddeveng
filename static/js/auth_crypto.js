/**
 * Client-Side Encrypted Admin Password Verification Module
 * Implements PBKDF2-HMAC-SHA256 key derivation, HMAC-SHA256 challenge proof,
 * and Encrypt-then-MAC (HMAC-SHA256-CTR) envelope encryption.
 * Plaintext password never leaves the browser and is never stored in client code.
 */
(function (global) {
    "use strict";

    const textEncoder = new TextEncoder();

    function hexToBytes(hex) {
        const clean = String(hex || "").trim();
        const out = new Uint8Array(clean.length / 2);
        for (let i = 0; i < out.length; i++) {
            out[i] = parseInt(clean.substr(i * 2, 2), 16);
        }
        return out;
    }

    function bytesToHex(bytes) {
        let hex = "";
        for (let i = 0; i < bytes.length; i++) {
            hex += bytes[i].toString(16).padStart(2, "0");
        }
        return hex;
    }

    function toBase64Url(bytes) {
        let binary = "";
        for (let i = 0; i < bytes.length; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    }

    function concatBytes(a, b) {
        const out = new Uint8Array(a.length + b.length);
        out.set(a, 0);
        out.set(b, a.length);
        return out;
    }

    function uint32BE(num) {
        return new Uint8Array([
            (num >>> 24) & 0xff,
            (num >>> 16) & 0xff,
            (num >>> 8) & 0xff,
            num & 0xff
        ]);
    }

    function randomBytes(len) {
        const buf = new Uint8Array(len);
        if (global.crypto && typeof global.crypto.getRandomValues === "function") {
            global.crypto.getRandomValues(buf);
        } else {
            for (let i = 0; i < len; i++) {
                buf[i] = Math.floor(Math.random() * 256);
            }
        }
        return buf;
    }

    // Pure-JS SHA-256 / HMAC-SHA256 / PBKDF2 fallback for insecure non-HTTPS HTTP origins
    const SHA256_K = new Uint32Array([
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]);

    function sha256Fallback(msgBytes) {
        const bitLen = msgBytes.length * 8;
        const padLen = ((56 - ((msgBytes.length + 1) % 64)) + 64) % 64;
        const padded = new Uint8Array(msgBytes.length + 1 + padLen + 8);
        padded.set(msgBytes, 0);
        padded[msgBytes.length] = 0x80;
        const view = new DataView(padded.buffer);
        view.setUint32(padded.length - 4, bitLen >>> 0, false);
        view.setUint32(padded.length - 8, Math.floor(bitLen / 0x100000000), false);

        let h0 = 0x6a09e667, h1 = 0xbb67ae85, h2 = 0x3c6ef372, h3 = 0xa54ff53a;
        let h4 = 0x510e527f, h5 = 0x9b05688c, h6 = 0x1f83d9ab, h7 = 0x5be0cd19;
        const w = new Uint32Array(64);
        const rotr = (x, n) => (x >>> n) | (x << (32 - n));

        for (let i = 0; i < padded.length; i += 64) {
            for (let t = 0; t < 16; t++) {
                w[t] = view.getUint32(i + t * 4, false);
            }
            for (let t = 16; t < 64; t++) {
                const s0 = rotr(w[t - 15], 7) ^ rotr(w[t - 15], 18) ^ (w[t - 15] >>> 3);
                const s1 = rotr(w[t - 2], 17) ^ rotr(w[t - 2], 19) ^ (w[t - 2] >>> 10);
                w[t] = (w[t - 16] + s0 + w[t - 7] + s1) >>> 0;
            }
            let a = h0, b = h1, c = h2, d = h3, e = h4, f = h5, g = h6, h = h7;
            for (let t = 0; t < 64; t++) {
                const S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
                const ch = (e & f) ^ (~e & g);
                const temp1 = (h + S1 + ch + SHA256_K[t] + w[t]) >>> 0;
                const S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
                const maj = (a & b) ^ (a & c) ^ (b & c);
                const temp2 = (S0 + maj) >>> 0;
                h = g; g = f; f = e; e = (d + temp1) >>> 0;
                d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
            }
            h0 = (h0 + a) >>> 0; h1 = (h1 + b) >>> 0; h2 = (h2 + c) >>> 0; h3 = (h3 + d) >>> 0;
            h4 = (h4 + e) >>> 0; h5 = (h5 + f) >>> 0; h6 = (h6 + g) >>> 0; h7 = (h7 + h) >>> 0;
        }
        const out = new Uint8Array(32);
        const outView = new DataView(out.buffer);
        [h0, h1, h2, h3, h4, h5, h6, h7].forEach((val, idx) => outView.setUint32(idx * 4, val, false));
        return out;
    }

    function hmacSha256Fallback(keyBytes, msgBytes) {
        const blockSize = 64;
        let key = keyBytes.length > blockSize ? sha256Fallback(keyBytes) : keyBytes;
        const ipad = new Uint8Array(blockSize);
        const opad = new Uint8Array(blockSize);
        ipad.fill(0x36);
        opad.fill(0x5c);
        for (let i = 0; i < key.length; i++) {
            ipad[i] ^= key[i];
            opad[i] ^= key[i];
        }
        return sha256Fallback(concatBytes(opad, sha256Fallback(concatBytes(ipad, msgBytes))));
    }

    function pbkdf2Sha256Fallback(passwordBytes, saltBytes, iterations) {
        let u = hmacSha256Fallback(passwordBytes, concatBytes(saltBytes, uint32BE(1)));
        const out = new Uint8Array(u);
        for (let i = 1; i < iterations; i++) {
            u = hmacSha256Fallback(passwordBytes, u);
            for (let j = 0; j < 32; j++) {
                out[j] ^= u[j];
            }
        }
        return out;
    }

    async function derivePbkdf2Key(password, salt, iterations) {
        const pwBytes = textEncoder.encode(password);
        const saltBytes = textEncoder.encode(salt);
        if (global.crypto && global.crypto.subtle) {
            const baseKey = await global.crypto.subtle.importKey(
                "raw",
                pwBytes,
                { name: "PBKDF2" },
                false,
                ["deriveBits"]
            );
            const bits = await global.crypto.subtle.deriveBits(
                {
                    name: "PBKDF2",
                    salt: saltBytes,
                    iterations: iterations,
                    hash: "SHA-256"
                },
                baseKey,
                256
            );
            return new Uint8Array(bits);
        }
        return pbkdf2Sha256Fallback(pwBytes, saltBytes, iterations);
    }

    async function computeHmacSha256(keyBytes, msgBytes) {
        if (global.crypto && global.crypto.subtle) {
            const cryptoKey = await global.crypto.subtle.importKey(
                "raw",
                keyBytes,
                { name: "HMAC", hash: "SHA-256" },
                false,
                ["sign"]
            );
            const sig = await global.crypto.subtle.sign("HMAC", cryptoKey, msgBytes);
            return new Uint8Array(sig);
        }
        return hmacSha256Fallback(keyBytes, msgBytes);
    }

    async function encryptPayloadEnvelope(transportKeyHex, payloadObj) {
        const transportKey = hexToBytes(transportKeyHex);
        const iv = randomBytes(16);
        const plainBytes = textEncoder.encode(JSON.stringify(payloadObj));
        const ciphertext = new Uint8Array(plainBytes.length);

        let offset = 0;
        let counter = 0;
        while (offset < plainBytes.length) {
            const block = await computeHmacSha256(transportKey, concatBytes(iv, uint32BE(counter)));
            const take = Math.min(block.length, plainBytes.length - offset);
            for (let i = 0; i < take; i++) {
                ciphertext[offset + i] = plainBytes[offset + i] ^ block[i];
            }
            offset += take;
            counter += 1;
        }

        const macTag = await computeHmacSha256(transportKey, concatBytes(iv, ciphertext));
        return `ENC-V1.${toBase64Url(iv)}.${toBase64Url(ciphertext)}.${toBase64Url(macTag)}`;
    }

    async function verifyAdminPasswordEncrypted(password, targetUrl) {
        const cleanPassword = String(password || "").trim();
        if (!cleanPassword) {
            return {
                ok: false,
                status: 400,
                data: { success: false, error: "Please enter the admin password." }
            };
        }

        const challengeRes = await fetch("/api/auth/challenge", {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        });
        if (!challengeRes.ok) {
            return {
                ok: false,
                status: challengeRes.status,
                data: { success: false, error: "Unable to initialize encrypted verification challenge." }
            };
        }

        const challenge = await challengeRes.json();
        const pwKeyBytes = await derivePbkdf2Key(cleanPassword, challenge.salt, challenge.iterations);
        const proofBytes = await computeHmacSha256(pwKeyBytes, textEncoder.encode(challenge.nonce));
        const proofHex = bytesToHex(proofBytes);

        const encryptedToken = await encryptPayloadEnvelope(challenge.transport_key, {
            proof: proofHex,
            nonce: challenge.nonce,
            ts: Date.now()
        });

        const verifyRes = await fetch("/api/verify-site-password", {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                encrypted_token: encryptedToken,
                target: targetUrl || window.location.pathname
            })
        });
        const verifyData = await verifyRes.json();
        return {
            ok: verifyRes.ok,
            status: verifyRes.status,
            data: verifyData
        };
    }

    global.FDEAuthCrypto = {
        verifyAdminPasswordEncrypted: verifyAdminPasswordEncrypted
    };
})(window);
