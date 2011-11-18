from reader import PelFile
import Combiner

def load(runs):
    paths = ["C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/%04i/Manifest.xml"
             % run for run in runs]
    return Combiner.load(paths)


def export(runs,sortby,flipper,minmon=16):
    data = load(runs)

    keys = data.keys()

    values = set([x[sortby] for x in keys])

    base = "C:/Documents and Settings/sesaadmin/My Documents/Neutron Data/%04i/" % runs[-1]

    for value in values:
        ups = [x for x in keys if x[flipper][0] != '-' 
               and x[sortby] == value]
        downs = [x for x in keys if x[flipper][0] == '-' 
                  and x[sortby] == value]
        Combiner.save(base+value+"up_temp.pel",
                      minmon,
                      ups,
                      data)
        Combiner.save(base+value+"down_temp.pel",
                      minmon,
                      downs,
                      data)
