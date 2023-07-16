# Bachelor's Degree project backend
This is the repository containing the back-end of my bachelor's degree project. The back-end uses the following frameworks:
* [FastAPI](https://fastapi.tiangolo.com/)
* [TFLearn](http://tflearn.org/)

The application has more use cases that can be observed in the following use case diagram (which is in romanian language):
![Use-case diagram](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/diagrams/use_case/Application's%20use%20cases.png)

This repository contains:
* Microservices' [source code](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/tree/main/src)
* [Script](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/docker_scripts/docker_main.py) to start the project locally (every microservice being encapsulated in a process)
* [Script](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/main.py) for managing the Docker Swarm encapsulated application (every microservice in its own Docker container)
* [__Dockerfiles__ and __requirements.txt__](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/tree/main/docker_images) for every microservice

## Back-end architecture
The application has been designed by creating a [microservice diagram](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/diagrams/microservice/Full%20system.png).
To make it easier to be understood, the diagram was split into more microservice diagrams, one for each system component.
The diagrams also contain:
* Microservices' contracts
* Each message's content
* Microservices that are not part of the presented component but who interact with it
* Message oriented middlewares' topics/queues (RabbitMq and Redis) represented as microservices
 
### Presentation component
![Presentation component diagram](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/diagrams/microservice/Presentation.png)

The presentation component contains only 3 RESTful microservices that mediate the interaction between the client and:
* the database ([DatabaseAPI](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/persistence/DatabaseAPI.py) microservice)
* song genre computation component (SongAdderController microservice)
* web crawling component (CrawlerManagementController microservice)

### Song genre computation component
![Song genre computation component diagram](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/diagrams/microservice/Genre%20computation%20pipeline.png)

The song genre computation component contains microservices for every part of the genre computation process presented in the [project that contains the CNN traininig/validation/testing logic](https://github.com/PetruBabiuc/MusicGenrePredictorDnnTrainer). The steps taken for genre computation are the following:
1. Create song's spectrogram (using [SpectrogramMaker](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/business/genre_predictor_pipeline/SpectrogramMaker.py) microservice)
2. Slice the spectrogram in 128x128 fragments (using [SpectrogramSlicer](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/business/genre_predictor_pipeline/SpectrogramSlicer.py) microservice)
3. For each slice get the probability of each genre (using [SliceGenrePredictor](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/business/genre_predictor_pipeline/SliceGenrePredictor.py) microservice)
4. For each slice compute the genre with highest probability (using [SliceDataProcessor](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/business/genre_predictor_pipeline/SliceDataProcessor.py) microservice)
5. Compute song's genre that is the genre with the most occurences in slices' genres (using [SliceGenreAggregator](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/business/genre_predictor_pipeline/SliceGenreAggregator.py) microservice)

The GenreComputerRequestManager simplifies component's usage for the presentation and web crawling components. This component uses microservice choreography.

### Web crawling component
![Web crawling component microservice diagram](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/diagrams/microservice/Crawler.png)

This component has the purpose to crawl a web domain specified by the user, on demand, in sessions. It also provides a cost control feature by letting the user limit the number of resources traversed in the process and the song genre computations. The component has a similar structure to other web crawlers (such as [Scrapy](https://scrapy.org/)), containing microservices for:
* Traversing the web domain and finding the desired items (songs' urls, using [Spider](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/business/crawler/Mp3SpiderMicroservice.py) microservice)) 
* Processing the items of interest (computing songs' genres, using [SongUrlProcessor](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/business/crawler/Mp3ProcessorMicroservice.py) microservice)
* Orchestrating the crawling process ([CrawlerEngine](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/business/crawler/CrawlerEngine.py) microservice)

The component traverses the web domain seeking web resources having the __Content-Type__ attribute of value __audio/mpeg__ or __text/html__. The __Content-Type__ of each resurse is obtained making a __HEAD HTTP Request__. The component stores songs' urls whose genres:
* are not desired by the user at the moment
* are not computed yet (because of the user's specified maximum genre computations)

The web resources already touched by the crawler are stored in a [Bloom Filter](https://github.com/prashnts/pybloomfiltermmap3).
The web crawling process tries to be polite by respecting __robots.txt__ files.
The component has the following activity diagram:

![Web crawling component activity diagram](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/diagrams/activity/Crawler.png)

### Song validation component
![Song validation component diagram](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/diagrams/microservice/Song%20validation.png)
This component verifies that the songs uploaded by the users/found on the internet are truly songs. Sometimes even if file's __Content-Type__ is __audio/mpeg__ or extension is MP3, the file may not be a valid MP3 song. The component also rejects too long or too short songs.

### Persistence component
![Persistence component diagram](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/diagrams/microservice/Persistence.png)

The component only contains the RESTful microservice named [DatabaseAPI](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/src/persistence/DatabaseAPI.py) and the MariaDB database.
The database has the following ER diagram:

![Database's ER diagram](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/blob/main/diagrams/ER/Database.png)

## More information
Microservices' Docker Images can be found [this DockerHub repository](https://hub.docker.com/repository/docker/petrubabiuc/licenta/general).
The two other projects that are composing my bachelor's degree project are:
1. [Application's front-end repository](https://github.com/PetruBabiuc/BachelorsDegreeFrontEnd)
2. [CNN training/validation/testing repository](https://github.com/PetruBabiuc/MusicGenrePredictorDnnTrainer)

The DNN used can be downloaded from [here](https://drive.google.com/file/d/1ZVZNSOMlAHZFPhuFQ-aXEDd2vy7sLHVl/view?ts=64b3948b).
Class diagrams for each microservice can be found [here](https://github.com/PetruBabiuc/MusicGenreComputationMicroservices/tree/main/diagrams/class).
