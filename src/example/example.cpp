#include <pybind11/pybind11.h>

namespace py = pybind11;

void print(const char* s) {
  printf("%s\n", s);
}

long add(long a, long b) {
  return a + b;
}

PYBIND11_MODULE(example, m) {
  m.doc() = "A minimal module.";
  m.def("print", &print, "Print something.", py::arg("s"));
  m.def("add", &add, "Add two numbers.", py::arg("a"), py::arg("b"));
}
