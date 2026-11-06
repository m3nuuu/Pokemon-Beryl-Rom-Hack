/* Headless mGBA runner for checking the ROM.
 *   play ROM SCRIPT
 * SCRIPT lines: "wait N" | "hold KEYS N" (keys: A B L R S=start E=select U D <  >) |
 *               "tap KEYS [N]" (press 2 frames, then release N frames, default 20) |
 *               "shot FILE.ppm" | "mash N" (tap A every 20 frames, N times) |
 *               "save FILE" (savestate) | "load FILE" (savestate)
 */
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/core/serialize.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void quiet(struct mLogger *l, int c, enum mLogLevel lv, const char *f, va_list a) { (void)l; (void)c; (void)lv; (void)f; (void)a; }
static struct mLogger logger = { .log = quiet };
static struct mCore *core;
static color_t *buf;
static unsigned W, H;

static uint32_t keys(const char *s) {
    uint32_t k = 0;
    for (; *s; s++) switch (*s) {
        case 'A': k |= 1; break; case 'B': k |= 2; break; case 'E': k |= 4; break; case 'S': k |= 8; break;
        case '>': k |= 16; break; case '<': k |= 32; break; case 'U': k |= 64; break; case 'D': k |= 128; break;
        case 'R': k |= 256; break; case 'L': k |= 512; break;
    }
    return k;
}

static void frames(uint32_t k, int n) { core->setKeys(core, k); while (n-- > 0) core->runFrame(core); }

static void shot(const char *path) {
    FILE *f = fopen(path, "wb");
    fprintf(f, "P6 %u %u 255\n", W, H);
    for (unsigned i = 0; i < W * H; i++) {
        uint32_t c = buf[i];
        unsigned char px[3] = { c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF };
        fwrite(px, 1, 3, f);
    }
    fclose(f);
}

int main(int argc, char **argv) {
    if (argc < 3) return 1;
    mLogSetDefaultLogger(&logger);
    core = mCoreFind(argv[1]);
    if (!core || !core->init(core)) return 2;
    mCoreInitConfig(core, NULL);
    core->desiredVideoDimensions(core, &W, &H);
    buf = calloc(W * H, BYTES_PER_PIXEL);
    core->setVideoBuffer(core, buf, W);
    if (!mCoreLoadFile(core, argv[1])) return 3;
    core->reset(core);
    FILE *s = fopen(argv[2], "r");
    char line[512];
    while (fgets(line, sizeof line, s)) {
        char cmd[32] = "", a[256] = "";
        int n = -1;
        if (sscanf(line, "%31s %255s %d", cmd, a, &n) < 1 || cmd[0] == '#') continue;
        if (!strcmp(cmd, "wait")) frames(0, atoi(a));
        else if (!strcmp(cmd, "hold")) frames(keys(a), n);
        else if (!strcmp(cmd, "tap")) { frames(keys(a), 2); frames(0, n < 0 ? 20 : n); }
        else if (!strcmp(cmd, "mash")) for (int i = atoi(a); i > 0; i--) { frames(1, 2); frames(0, 20); }
        else if (!strcmp(cmd, "shot")) shot(a);
        else if (!strcmp(cmd, "save")) { struct VFile *vf = VFileOpen(a, O_CREAT | O_TRUNC | O_WRONLY); mCoreSaveStateNamed(core, vf, SAVESTATE_ALL); vf->close(vf); }
        else if (!strcmp(cmd, "load")) { struct VFile *vf = VFileOpen(a, O_RDONLY); mCoreLoadStateNamed(core, vf, SAVESTATE_ALL); vf->close(vf); }
    }
    core->deinit(core);
    return 0;
}
