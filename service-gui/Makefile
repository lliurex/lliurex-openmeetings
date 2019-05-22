

#color scheme
COLOR_NONE=\x1b[0m
COLOR_COMPILE=\x1b[32;01m
COLOR_BUILD=\x1b[35;01m
COLOR_CLEAN=\x1b[31;01m

#application name
APP_NAME=lliurex-openmeetings-service-gui

#libraries
LIBS=gtkmm-3.0

#objects
OBJECTS=service-gui.o

#cflags
LIBS_CFLAGS=`pkg-config $(LIBS) --cflags`

#link
LIBS_LINK=`pkg-config $(LIBS) --libs`	

#compilation flags
CCFLAGS=-std=c++0x $(LIBS_CFLAGS)

ifdef DEBUG
CCFLAGS+=-g
else
CCFLAGS+=-O2
endif


all: $(APP_NAME)

$(APP_NAME): $(OBJECTS)
	@echo -e '$(COLOR_BUILD)* Building [$@]$(COLOR_NONE)'
	g++ -o $(APP_NAME) $(OBJECTS) $(LIBS_LINK)


%.o : %.cpp
	@echo -e '$(COLOR_COMPILE)* Compiling [$<]$(COLOR_NONE)'
	g++ -c $< $(CCFLAGS)

%.o : %.c
	@echo -e '$(COLOR_COMPILE)* Compiling [$<]$(COLOR_NONE)'
	g++ -c $< $(CCFLAGS)

clean:
	@echo -e '$(COLOR_BUILD)* Cleaning$(COLOR_NONE)'
	rm -f $(APP_NAME)
	rm -f $(OBJECTS)
	

