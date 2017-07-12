# Livewire Simple Delegation Switcher

This application allows you to simply switch between different Livewire Sources (Inputs) and send them to a single Livewire Destination (Output). It's designed to be used as a simple studio delegation switcher.

![Livewire Simple Delegation Switcher - Screenshot](https://mediarealm.com.au/wp-content/uploads/2017/07/Livewire-Simple-Delegation-Switcher-Screenshot.png)

You could use the PathfinderPC software. However, most small radio station's don't have the budget to buy this. If all you need to do is switch between a couple of different sources, Pathfinder can seem overkill.

This application relies on the Livewire Routing Protocol, so most Axia Livewire devices are supported. To support LWRP, we make use of the following libraries:

* [Livewire Routing Protocol Client](https://github.com/anthonyeden/Livewire-Routing-Protocol-Client)
* [Axia Livewire Stream Address Helper](https://github.com/anthonyeden/Axia-Livewire-Stream-Address-Helper)

This software has been developed by Anthony Eden (https://mediarealm.com.au/).

## Getting Started

1. Download the latest version from the "[Releases](https://github.com/anthonyeden/Livewire-Simple-Delegation-Switcher/releases)" page
2. Unzip the files someplace on your computer
3. Rename 'config-sample.json' to 'config.json'
4. Edit config.json to meet your needs

 * You'll need to include the IP Address of your Output Node, the physical output number on your Node, and Livewire Channel Numbers for each source

5. Run LW-Delegation-Switcher.exe

If all has gone well, you'll now be able to switch the source to your destination. The source highlighted in "Red" is the currently active source.

## License

This software has been released as open source software. You're free to use and modify this software, but no liability can be accepted by the developer.

Please read the license agreement.

## Contributing

Contributions are welcomed. Feel free to submit a pull request to fix bugs or add additional functionality to this application.
