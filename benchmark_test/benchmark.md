# Сравнение производительности Nginx и Gunicorn

- Размер документа: 30 KB
- Количество запросов: 100
- Количество подключений: 5

| Метрика | Nginx (статика) | Gunicorn (статика) | Gunicorn (динамика) | Nginx+Gunicorn (без кэша) | Nginx+Gunicorn (с кэшем) |
|---------|-----------------|-------------------|-------------------|-------------------------|-------------------------|
| **Время выполнения теста** | 0.024 сек | 0.048 сек | 0.163 сек | 0.199 сек | 0.046 сек |
| **Запросов в секунду** | 4090.48 | 2094.81 | 612.14 | 502.66 | 2162.58 |
| **Время на запрос (среднее)** | 1.222 мс | 2.387 мс | 8.168 мс | 9.947 мс | 2.312 мс |
| **Скорость передачи** | 120345.64 KB/сек | 61269.13 KB/сек | 18435.49 KB/сек | 15151.59 KB/сек | 65185.83 KB/сек |

### Насколько быстрее отдается статика по сравнению с WSGI?
Почти в 2 раза быстрее

### Во сколько раз ускоряет работу proxy_cache?
В 4 раза

# Отдача статического документа напрямую через nginx;
```bash
ab -n 100 -c 5 http://localhost/benchmark_test/static
```
```bash
(venv) kathrine@Viva:~/vuz/web-vk-education$ ab -n 100 -c 5 http://localhost/benchmark_test/static
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient).....done


Server Software:        nginx/1.29.3
Server Hostname:        localhost
Server Port:            80

Document Path:          /benchmark_test/static
Document Length:        29831 bytes

Concurrency Level:      5
Time taken for tests:   0.024 seconds
Complete requests:      100
Failed requests:        0
Total transferred:      3012700 bytes
HTML transferred:       2983100 bytes
Requests per second:    4090.48 [#/sec] (mean)
Time per request:       1.222 [ms] (mean)
Time per request:       0.244 [ms] (mean, across all concurrent requests)
Transfer rate:          120345.64 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:     1    1   0.5      1       6
Waiting:        0    1   0.4      1       5
Total:          1    1   0.5      1       6

Percentage of the requests served within a certain time (ms)
  50%      1
  66%      1
  75%      1
  80%      1
  90%      1
  95%      1
  98%      2
  99%      6
 100%      6 (longest request)
```
# Отдача статического документа напрямую через gunicorn
```bash
ab -n 100 -c 5 http://127.0.0.1:8081/static
```
```bash
(venv) kathrine@Viva:~/vuz/web-vk-education/gunicorn$ ab -n 100 -c 5 http://127.0.0.1:8081/static
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        gunicorn
Server Hostname:        127.0.0.1
Server Port:            8081

Document Path:          /static
Document Length:        29831 bytes

Concurrency Level:      5
Time taken for tests:   0.048 seconds
Complete requests:      100
Failed requests:        0
Total transferred:      2995000 bytes
HTML transferred:       2983100 bytes
Requests per second:    2094.81 [#/sec] (mean)
Time per request:       2.387 [ms] (mean)
Time per request:       0.477 [ms] (mean, across all concurrent requests)
Transfer rate:          61269.13 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       1
Processing:     1    2   0.6      2       5
Waiting:        1    2   0.6      2       4
Total:          1    2   0.6      2       5

Percentage of the requests served within a certain time (ms)
  50%      2
  66%      2
  75%      3
  80%      3
  90%      3
  95%      3
  98%      4
  99%      5
 100%      5 (longest request)
```
# Отдача динамического документа напрямую через gunicorn
```bash
ab -n 100 -c 5 http://127.0.0.1:8081/dynamic
```
```bash
(venv) kathrine@Viva:~/vuz/web-vk-education/gunicorn$ ab -n 100 -c 5 http://127.0.0.1:8081/dynamic
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        gunicorn
Server Hostname:        127.0.0.1
Server Port:            8081

Document Path:          /dynamic
Document Length:        30720 bytes

Concurrency Level:      5
Time taken for tests:   0.163 seconds
Complete requests:      100
Failed requests:        0
Total transferred:      3083900 bytes
HTML transferred:       3072000 bytes
Requests per second:    612.14 [#/sec] (mean)
Time per request:       8.168 [ms] (mean)
Time per request:       1.634 [ms] (mean, across all concurrent requests)
Transfer rate:          18435.49 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:     6    8   0.6      8       9
Waiting:        6    7   0.6      7       9
Total:          6    8   0.6      8       9

Percentage of the requests served within a certain time (ms)
  50%      8
  66%      8
  75%      8
  80%      8
  90%      8
  95%      9
  98%      9
  99%      9
 100%      9 (longest request)
```

# Отдача динамического документа через проксирование запроса с nginx на gunicorn
``` bash
ab -n 100 -c 5 http://localhost/gunicorn/dynamic
```
``` bash
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient).....done


Server Software:        nginx/1.29.3
Server Hostname:        localhost
Server Port:            80

Document Path:          /gunicorn/dynamic
Document Length:        30720 bytes

Concurrency Level:      5
Time taken for tests:   0.199 seconds
Complete requests:      100
Failed requests:        0
Total transferred:      3086600 bytes
HTML transferred:       3072000 bytes
Requests per second:    502.66 [#/sec] (mean)
Time per request:       9.947 [ms] (mean)
Time per request:       1.989 [ms] (mean, across all concurrent requests)
Transfer rate:          15151.59 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:     7    9   1.9      9      22
Waiting:        7    9   1.9      8      22
Total:          7    9   1.9      9      22

Percentage of the requests served within a certain time (ms)
  50%      9
  66%      9
  75%     10
  80%     10
  90%     12
  95%     13
  98%     14
  99%     22
 100%     22 (longest request)
```


# Отдача динамического документа через проксирование запроса с nginx на gunicorn, при кэшировние ответа на nginx (proxy cache).
```bash
ab -n 100 -c 5 http://localhost/gunicorn/dynamic
```
```bash
(venv) kathrine@Viva:~/vuz/web-vk-education$ ab -n 100 -c 5 http://localhost/gunicorn/dynamic
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient).....done


Server Software:        nginx/1.29.3
Server Hostname:        localhost
Server Port:            80

Document Path:          /gunicorn/dynamic
Document Length:        30720 bytes

Concurrency Level:      5
Time taken for tests:   0.046 seconds
Complete requests:      100
Failed requests:        0
Total transferred:      3086600 bytes
HTML transferred:       3072000 bytes
Requests per second:    2162.58 [#/sec] (mean)
Time per request:       2.312 [ms] (mean)
Time per request:       0.462 [ms] (mean, across all concurrent requests)
Transfer rate:          65185.83 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:     1    1   2.4      1      25
Waiting:        1    1   2.4      1      24
Total:          1    1   2.4      1      25

Percentage of the requests served within a certain time (ms)
  50%      1
  66%      1
  75%      1
  80%      1
  90%      1
  95%      1
  98%      1
  99%     25
 100%     25 (longest request)
```
