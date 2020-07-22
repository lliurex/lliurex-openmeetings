

	
all:
	make -C setup-gui/ $@
	make -C svg/ $@
	
clean:
	make -C setup-gui/ $@
	make -C svg/ $@

pot:
	xgettext -d lliurex-openmeetings-setup -s --keyword=T -o lliurex-openmeetings-setup.pot setup-gui/setup-gui.cpp service-gui/service-gui.cpp setup-gui/interface.glade service-gui/interface.glade
