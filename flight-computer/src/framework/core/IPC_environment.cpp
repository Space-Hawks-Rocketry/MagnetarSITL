#include "framework/core/IPC_environment.hpp"
#include <format>
#include <string.h>
#include <iostream>


IPC_Environment::IPC_Environment() {
  context = zmq::context_t();
  socket = zmq::socket_t(context, zmq::socket_type::rep);
}

void IPC_Environment::start(int port) {
  socket.bind(std::format("tcp://localhost:{}", port));
}

void IPC_Environment::close() {
  socket.close();
  context.close();
}

std::optional<json> IPC_Environment::recvJSON() {
  zmq::message_t msg;
  auto result = socket.recv(msg);

  if (result) {
    std::string msg_string(static_cast<char*>(msg.data()), msg.size());
    try {
      return json::parse(msg_string);
    } catch (const json::parse_error& e) {
      std::cerr << "JSON Parsing error: " << e.what() << std::endl;
      return {};
    }
  }
  return {};
}

void IPC_Environment::sendJSON(json msg_json) {
  std::string msg_string = msg_json.dump();
  socket.send(zmq::buffer(msg_string), zmq::send_flags::none);
}