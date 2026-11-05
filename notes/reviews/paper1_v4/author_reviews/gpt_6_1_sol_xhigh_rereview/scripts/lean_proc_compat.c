/* Environment compatibility only: this host exposes /proc/self/exe but not
 * /proc/<own numeric pid>/exe. Lean4.35.0 uses the latter in IO.appPath.
 * Redirect only that exact own-process path to the equivalent self path.
 * No kernel, elaborator, proof term, axiom or author source is changed.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
ssize_t readlink(const char *path, char *buf, size_t size) {
    static ssize_t (*original)(const char *, char *, size_t);
    if (!original) original = dlsym(RTLD_NEXT, "readlink");
    char own[80];
    snprintf(own, sizeof own, "/proc/%d/exe", (int)getpid());
    return original(strcmp(path, own) == 0 ? "/proc/self/exe" : path, buf, size);
}
