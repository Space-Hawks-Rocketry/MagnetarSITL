## Define build and run commands for SITL framework

build:
	cmake -S flight-computer -B flight-computer/build
	cmake --build flight-computer/build

run:
	-pkill -f FlightComputer || true
	-pkill -f "python3 environment/SITL_main.py" || true

	./flight-computer/build/FlightComputer & \
	python3 environment/SITL_main.py

sitl:
	$(MAKE) build
	$(MAKE) run

clean:
	-pkill -f FlightComputer || true
	-pkill -f "python3 environment/SITL_main.py" || true
	rm -rf flight-computer/build