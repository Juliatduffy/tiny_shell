#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>

int main(int argc, char** argv) {
    int fds[2];
    pipe(fds);

    char* writer_args[] = {argv[1], NULL};
    char* reader_args[] = {argv[argc-1], NULL};
    char* env[] = {NULL};
    
    // First child
    if(fork() == 0) {
      dup2(fds[1],1);
      if(execve(writer_args[0], writer_args, env) == -1)
      exit(1);
      close(fds[1]);
    }

    int newfds[2];
    char* new_args[] = {0, NULL};
      pipe(newfds);
      new_args[0] = argv[i];
      if(fork() == 0) {
        close(fds[1]);
        dup2(fds[0], 0);
        dup2(newfds[1],1);
        if(execve(new_args[0], new_args, env) == -1)
        exit(1);
        close(newfds[1]);
      }
      close(newfds[1]);
    }

    // Third child
    if(fork() == 0) {
      close(fds[1]);
      close(reader_args[1]);
      dup2(newfds[0],0);
      if(execve(reader_args[0], new_args, env) == -1)
        exit(1);
    }
    
    // maybe remove
    close(fds[1]);

    // Parent
    int status;
    wait(&status);
    wait(&status);
    wait(&status);
}
