/* SPDX-License-Identifier: LGPL-2.1-or-later
 * POSIX diagnostic caller of the unchanged VLC process API.
 * Run only through the independent process-group deadline wrapper.
 */
#ifdef HAVE_CONFIG_H
# include "config.h"
#endif
#include <vlc_common.h>
#include <vlc_process.h>
#include <signal.h>
#include <unistd.h>
#include <sys/wait.h>

static void ignore_termination(int signal_number)
{
    (void)signal_number;
    static const char event[] = "child_sigterm_ignored\n";
    (void)write(STDERR_FILENO, event, sizeof(event) - 1);
}

static int child(bool ignore)
{
    struct sigaction action = {0};
    action.sa_handler = ignore ? ignore_termination : SIG_DFL;
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGTERM, &action, NULL) != 0)
        return 3;
    fprintf(stderr, "child_ready pid=%ld pgid=%ld ignores_sigterm=%d\n",
            (long)getpid(), (long)getpgrp(), ignore);
    fflush(stderr);
    if (write(STDOUT_FILENO, "R", 1) != 1)
        return 4;
    for (;;)
        pause();
}

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "child-ignore") == 0)
        return child(true);
    if (argc == 2 && strcmp(argv[1], "child-default") == 0)
        return child(false);
    if (argc != 2 || (strcmp(argv[1], "ignore") != 0 &&
                      strcmp(argv[1], "default") != 0))
    {
        fprintf(stderr, "Usage: process-probe {default|ignore}\n");
        return 2;
    }
    /* The launcher must put this process in a new, dedicated group/session. */
    if (getpgrp() != getpid())
    {
        fprintf(stderr, "Refusing execution outside dedicated process group\n");
        return 2;
    }
    setvbuf(stdout, NULL, _IOLBF, 0);
    const char *child_args[] = {
        strcmp(argv[1], "ignore") == 0 ? "child-ignore" : "child-default"
    };
    struct vlc_process *process = vlc_process_Spawn(argv[0], 1, child_args);
    if (process == NULL)
    {
        puts("{\"event\":\"spawn_failed\"}");
        return 3;
    }
    uint8_t ready = 0;
    ssize_t count = vlc_process_fd_Read(process, &ready, 1, 2000);
    if (count != 1 || ready != 'R')
    {
        puts("{\"event\":\"readiness_failed\"}");
        /* The outer launcher owns cleanup even if this termination blocks. */
        vlc_process_Terminate(process, true);
        return 4;
    }
    puts("{\"event\":\"termination_begin\"}");
    int status = vlc_process_Terminate(process, true);
    printf("{\"event\":\"termination_return\",\"raw_wait_status\":%d,"
           "\"signalled\":%d,\"signal\":%d}\n", status,
           status >= 0 && WIFSIGNALED(status),
           status >= 0 && WIFSIGNALED(status) ? WTERMSIG(status) : 0);
    return status >= 0 ? 0 : 5;
}
