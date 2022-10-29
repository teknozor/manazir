# :rabbit: Manazir :rabbit:

## A scalable and automatic anomaly and root cause analysis system
<!-- 
<kbd>
  <img src="https://user-images.githubusercontent.com/19171248/manazir.png"/>
</kbd> -->

<div>&nbsp;</div>

Manazir is inspired by many open source project such ass bunnybook for the backend architecture, thirdeye for automatic anomlay detection and root cause analysis, with the goal to implement Ebay Groot for event graph root cause analytics, and possibaly has been made scalable to support spark, dask, and ray using fugue project.

The goal is to automate the anomaly detection on large scale sensor enviorment and possibly design a pipeline that's human centred to augement organaization capability manage the increasing demand without breaking their operating model.

Included features:
- metadata layer for data autodiscovery
- Anomaly detection engine
- Root cause analytics and knowledge graph for an event based RCA
- Scalable processing engine
- ... and potentially being possible to run auto detection on stream. 

Tech stack:
- Python 3.8 + FastAPI
- PostgreSQL 13 + async SQLAlchemy (Core) + asyncpg driver
- Neo4j graph db for relationships between users and fast queries
- Redis for caching and Pub/Sub
- Socket.IO for chat and notifications
- Jwt + refresh tokens rotation for authentication
- Docker + docker-compose to ease deployment and development  

<br/>
Feel free to contact me on LinkedIn for ideas, discussions and opportunities :slightly_smiling_face: https://www.linkedin.com/in/pietro-bassi/ 

## Scope of the project
**What Manazir is**: We created Manazir to have the opportunity to experiment with some technologies I wasn't familiar with (e.g. Neo4j). I love learning new ways to solve problems at scale and a small social network seemed a very good candidate to test a few interesting libraries and techniques.  
<br/>
**What Bunnybook isn't**: a production-ready social network with infinite scaling capabilities. Building a "production-ready social network" would require way more testing and refinement (e.g. some features scale while others don't, test coverage is not complete, chat is hidden in mobile-mode and the entire project is not particularly responsive etc.), but this is out of the scope of this small experiment.


## Quick start
#### Requirements
- OS: Linux, macOS, Windows 
- Install Docker (https://docs.docker.com/install/)
- (Linux only) Install docker-compose (https://docs.docker.com/compose/install/)
#### Deploy Bunnybook on your local machine
Open a shell and clone this repository:  
`git clone git@github.com:teknozor/manazir.git`  

Navigate inside project root folder:  
`cd manazir`  

Start all services:  
`docker-compose up`  

API documentation is hosted at:
http://localhost:8000/docs and http://localhost:8000/redoc
> Please note: after pulling new changes from this repo, remember to execute `docker-compose up --build` to recreate containers

## Developing
#### Requirements
- OS: Linux, macOS
- Install Docker (https://docs.docker.com/install/)
- (Linux only) Install docker-compose (https://docs.docker.com/compose/install/)
- Install Node v10.16.0 https://nodejs.org/en/, preferably using Nvm (https://github.com/nvm-sh/nvm)
- Install Python 3.8 (https://www.python.org/downloads/), preferably using pyenv (https://github.com/pyenv/pyenv)
- Install virtualenv (https://virtualenv.pypa.io/en/latest/)
#### Development setup
- Clone this repository, navigate inside root folder and execute `docker-compose -f docker-compose-dev.yml up` to start services (PostgreSQL, Neo4j, Redis, etc.)
> If you have other services running on your machine, port collisions are possibile: check docker-compose-dev.yml to see which ports are shared with host machine
- Navigate to "backend" folder and create a Python 3.8 virtual environment; activate it, execute `pip install -r requirements.txt`, run `python init_db.py` (to generate databases schemas and constraints) and then `python main.py` (backend default port: 8000)
- Navigate to "frontend" folder and install npm packages with `npm install`; start React development server with `npm start` (frontend default port: 3000)

Navigate to:
http://localhost:3000

#### Testing
To run integration tests, navigate to "backend" folder, activate virtualenv and execute:  
`pytest`  
This command brings up a new clean docker-compose environment (with services mapped on different ports so they don't collide with the ones declared inside docker-compose-dev.yml), executes integration tests and performs services teardown.
> To execute faster tests during development phase without leveraging the ad-hoc docker-compose environment, run  
> `DEV=true pytest`  
> while all the services are up and running: this will pollute you development database a bit with some test data, but it is much faster

## Architectural considerations
#### Authentication
Authentication is performed via JWT access tokens + JWT refresh tokens (which are rotated at every refresh and stored in the database in order to allow session banning): with appropriate secret-sharing mechanisms, this configuration prevents the need for backend services to call a stateful user session holder (e.g. Redis) on every API call.  
Access tokens are saved in localStorage whilst refresh token are stored inside secure, HTTP only cookies.  
Saving access tokens in localStorage is not ideal since it exposes them to XSS attacks, but this choice comes from early stages of development where I wanted to use the same access token to authenticate both API calls and websocket connections and I was leveraging a websocket library that wasn't able to read Cookies inside "on connect" event handler; now, since Socket.IO can access them, a nice and easy fix would be to store access tokens in secure Cookies as well.

#### Caching
There are 2 Redis instances - one for chat/notifications and one for caching - in order not to have a single point of failure: a crash of cache backend shouldn't affect messaging! This is also the reason why backend code ignores failed cache calls (it just logs them) and goes on querying PostgreSQL/Neo4j to preserve Bunnybook functionality.  
Most of caching follows Cache-Aside strategy. To store paginated results, only basic Redis data structures have been used, although I've also made some tests  with sorted sets (ranked by post/comment/message/... creation date) and more complex logic in order to handle frequently changing data collections.


#### Databases
Neo4j have been introduced alongside PostgreSQL to implement Groot like event graph for root cause analysis  in a convenient way.

Neo4j Bolt driver doesn't natively expose an async interface, so all calls are executed in separate threads (taken from a thread pool) not to block the main event loop. HTTP APIs + httpx could have been used to avoid the need for run_in_executor calls, at the cost of less convenient responses parsing and slightly worse performance (tested: still a valid solution in my opinion).  
<br/>
For PostgreSQL access, SQLAlchemy have been used asynchronously in "Core" mode; async "ORM" mode is quite new and - to use it correctly - some precautions must be taken to prevent implicit IO. Generally speaking, for CRUD-like apps (like Bunnybook) that don't involve a lot of business logic and complex objects interactions, We prefer to avoid ORMs and stick with query-builder libraries to have more control over the generated queries.

PostgreSQL connection pooling via pgbouncer is currently not used since encode/databases under the hood creates an asyncpg-managed connection pool; in order to increase scalability, a NullPool-like pool object should be used, overriding current encode/databases PostgreSQL backend adapter implementation.  
In addition, PostgreSQL "pg_trgm" module as well as "gin" indexes have been added to speed up text search queries.

#### Dependency Injection
Large use of dependency injection techniques in backend (injector), where  standard FastAPI DI framework has been extended to make it compatible with "injector" package using a small utility function. Although some people might consider the extensive use of DI in Python an overkill since you have module imports, I still prefer to use it to have better control over instances initialization, easier testing and clearer dependency graph.

#### Model
Backend model layer is made of pydantic classes, following the Anemic Domain Model pattern. Pydantic is a great way to represent domain model, ensuring continuous data validation and enforcing type hints at runtime. Regarding Anemic Domain Model, some people consider it an "anti-pattern": I respectfully disagree. Both Rich Domain Model and Anemic Domain Model have their reason to exist, what really matters is knowing why you are choosing one over the other and being aware of the pros/cons of each conceptual model.

## Development ideas and open issues
- cache notifications
- reimplement chat database schema to use a more "modern" approach, in order to leverage PostgreSQL 9.6+ recursive queries
- rate limit Socket.IO events
- store JWT access tokens the same way as JWT refresh tokens (secure + HTTP only + same site Cookies)
- take countermeasures against cache stampede (e.g. through locking)
- improve "RESTfulness" of profiles API
- increase test coverage, adding more integration tests, as well as unit and functional tests
