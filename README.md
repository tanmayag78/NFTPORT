# NFTPort Backend Test Assignment

### Getting NFTs

###NOTE:
1. When inserting the data, we must use Celery/RedisQueue so that user can get the response fast instead of waiting till all the contents are fetched. Didn't get the time to implement it.
2. I have used Synchronous calls only for this API as request was blocking many times. Also instead of fetching all pages and all examples I used only 1 page with 10 examples.
3. A snippet of asynchrononous code is there in nft_scrap.py file.
4. REST API is in Development mode.


Deploy REST API:
Clone the repo and move to the repo directory and run the below command
```
docker-compose up
```

###API Endpoints:

- GET /nft
  - Params-
    - token_id: NFT Token ID
    - contract_address: Contract Address
    - name: Name
- POST /nft
  - Payload
    - contract_address*

### API Run Examples:
- For Inserting NFTS
  - Payload Required- 
    - `contract_address*` 
  - Example
    - ```curl --request POST 'http://localhost:8000/nfts/' --header 'Content-Type: application/json' --data-raw '{"contract_address": "0x12d2d1bed91c24f878f37e66bd829ce7197e4d14"}'```


- For Retrieving NFTS
  - Params-
    - name
    - contract_address
    - token_id
  - Example- For Retrieving NFTs
    - ```curl --request GET 'http://localhost:8000/nfts/?contract_address=0x12d2d1bed91c24f878f37e66bd829ce7197e4d14&name=GalacticApe %231005'```
  - For Retrieving NFT
    - ```curl --request GET 'http://localhost:8000/nfts/?contract_address=0x12d2d1bed91c24f878f37e66bd829ce7197e4d14&token_id=1004'```



### Scaling - how would you do it?

1. As there are 100k+ transactions in the blockchain, we will use asynchronous architecture so that we can fetch the data in parallel.
2. We will store the media files in S3 and use CDN to serve it.
3. We will use a Redis cache to store the most frequently/recent accessed data so that if request comes for these data, then there is no db query.
4. Shard our Database for Load Management.
5. We can also have replicas of database for read, although in this case it will be difficult to manage.
6. Vertical and Horizontal scaling. Also use load balancer so that requests can be redirected by it. Instead we can use Kubernetes to manage multiple containers and openshift to manage Kubernetes clusters.
7. Using Rediqueue/Celery for messaging queue and asynchronous tasks.
8. Using indexes in Table column which will make search faster.
9. Using Nosql database instead of relational database or a layer of Nosql database over Relational Database. When data is entered in RDBMS, asynchronously trigger a job to index data in NoSql database.



