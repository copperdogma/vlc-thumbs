# Archive isolation boundary

General class: generated source metadata accidentally discovers an ancestor Git checkout. Git documentation requires a ceiling directory on the actual ancestor path: https://git-scm.com/docs/git/2.45.1 (GIT_CEILING_DIRECTORIES). The retained public recipe keeps its archive beneath outer, where its outer ceiling applies.

The first private archive-only adaptation instead extracted beside outer while leaving the ceiling at outer. This was a wrapper error. Source revision generation found the parent project repository and attempted to overwrite read-only archive src/revision.txt. The first351.37s attempt is FAILED and preserved; archive src/revision.txt remains8cd1b7c.

Decision: use archive001 as the common-ancestor ceiling for both outer and extracted/build. The exact Git rev-parse query in extracted now fails as intended before ordinary make resumes. No source patch, reconfigure, re-make-dist or feature disable. The one continuation has249s bound; no broader retry.

The ordinary Autotools archive contains67 of70 changed paths byte-exact. configure.ac undergoes its standard distribution date freeze. Two Meson entry files are omitted under the existing Autotools packaging boundary; root meson.build is also absent. This does not qualify a Meson archive build; the Git/format-patch submission includes all70 source paths.
