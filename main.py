from dataclasses import dataclass
from multiprocessing import Process
from time import sleep
from typing import Any
from src.business.SliceDataProcessor import SliceDataProcessor
from src.business.SliceGenreAggregator import SliceGenreAggregator
from src.business.SliceGenrePredictor import DebugSliceGenrePredictor, SliceGenrePredictor
from src.business.SpectrogramFilter import DebugSpectrogramFilter, SpectrogramFilter
from src.business.SpectrogramMaker import DebugSpectrogramMaker, SpectrogramMaker
from src.business.SpectrogramQueue import DebugSpectrogramQueue, SpectrogramQueue
from src.business.SpectrogramSlicer import DebugSpectrogramSlicer, SpectrogramSlicer
from src.presentation.Controller import DebugController, Controller


@dataclass
class ReplicationInfo:
    microservice_class: Any
    instances_number: int
    name: str
    args: tuple


def instantiate_and_run(microservice_class, args):
    microservice_class(*args).run()


if __name__ == '__main__':
    output_dir = 'debug_files/'
    dnn_path = 'dnn/musicDNN.tflearn'
    debug = False

    # The following microservices open ServerSocket(s) => Instantiate once at most:
    # Controller, SpectrogramFilter, SpectrogramQueue, SliceGenreAggregator
    if debug:
        microservices_info = (
            ReplicationInfo(DebugController, 1, 'Controller', (output_dir,)),
            ReplicationInfo(DebugSpectrogramMaker, 1, 'SpectrogramMaker', (output_dir,)),
            ReplicationInfo(DebugSpectrogramFilter, 1, 'SpectrogramFilter', (output_dir,)),
            ReplicationInfo(DebugSpectrogramQueue, 1, 'SpectrogramQueue', (output_dir,)),
            ReplicationInfo(DebugSpectrogramSlicer, 1, 'SpectrogramSlicer', (output_dir,)),
            ReplicationInfo(DebugSliceGenrePredictor, 1, 'SliceGenrePredictor', (dnn_path, output_dir)),
            ReplicationInfo(SliceDataProcessor, 1, 'SliceDataProcessor', ()),
            ReplicationInfo(SliceGenreAggregator, 1, 'SliceGenreAggregator', ())
        )
    else:
        microservices_info = (
            ReplicationInfo(Controller, 1, 'Controller', ()),
            ReplicationInfo(SpectrogramMaker, 3, 'SpectrogramMaker', ()),
            ReplicationInfo(SpectrogramFilter, 1, 'SpectrogramFilter', ()),
            ReplicationInfo(SpectrogramQueue, 1, 'SpectrogramQueue', ()),
            ReplicationInfo(SpectrogramSlicer, 3, 'SpectrogramSlicer', ()),
            ReplicationInfo(SliceGenrePredictor, 3, 'SliceGenrePredictor', (dnn_path,)),
            ReplicationInfo(SliceDataProcessor, 3, 'SliceDataProcessor', ()),
            ReplicationInfo(SliceGenreAggregator, 1, 'SliceGenreAggregator', ())
        )

    processes = []
    for info in microservices_info:
        for i in range(info.instances_number):
            name = f'{info.name}_{i}'
            new_args = info.args + (name,)
            processes.append(Process(target=instantiate_and_run,
                                     name=name,
                                     args=(info.microservice_class, new_args)))

    try:
        for p in processes:
            p.start()
            sleep(0.5)
        for p in processes:
            p.join()
    except BaseException:
        for p in processes:
            p.kill()
