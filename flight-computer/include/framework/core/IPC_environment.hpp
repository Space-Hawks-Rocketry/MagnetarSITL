#pragma once

#include <nlohmann/json.hpp>
#include <optional>
#include <zmq.hpp>

using json = nlohmann::json;

class IPC_Environment {
public:
  IPC_Environment();
  void start(int port);
  void close();
  std::optional<json> recvJSON();
  void sendJSON(json msg);

private:
  zmq::context_t context;
  zmq::socket_t socket;
};