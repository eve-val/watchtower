# Watchtower

## Development Install

 - install Vagrant
 - install Virtualbox (or maybe Vagrant will understand if you have some other
   virtualization tool, I don't know)
 - `cp Vagrantfile.example Vagrantfile` and edit to your liking
 - `vagrant up`
 - edit config.ini as appropriate
 - `vagrant ssh`
 - `run`

## Deployment

(aka the important bits of what the vagrant config does)

 - `cp config.example.ini config.ini` and edit as appropriate
 - `pip install -e .`
 - `python -m watchtower config.ini` to run
