# ruyiwebcrawl

### 1.web crawler cache

    I would like to asynchronous cache service with every single process.

### 2.centralized web proxy pool

    Because proxy pool data structure saved in memory, so can not run this service in multiprocess mode.
    But crawler cache need to run in multiprocess mode.
    So I want to deploy these two services separately in different processes.
    Or else I need to change proxy pool data structure in Redis or shared memory.
