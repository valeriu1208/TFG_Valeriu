class QuantumServer2:
    def __init__(self, host: str, qbits: int, shots: int, circuit_depth: int, qstorage: int):
        self.host = host
        self.qbits = qbits
        self.shots = shots
        self.circuit_depth = circuit_depth
        self.qstorage = qstorage
        self.available_resources = {
            "qbits": qbits,
            "shots": shots,
            "circuit_depth": circuit_depth,
            "qstorage": qstorage
        }
        self.requested_resources = {
            "qbits": 0,
            "shots": 0,
            "circuit_depth": 0,
            "qstorage": 0
        }
class TypeQ():
    server = QuantumServer2(
        host="192.168.1.200", 
        qbits=127, 
        shots=10000, 
        circuit_depth=5000, 
        qstorage= (127 * 10000 // 8)
    )
    server1 = QuantumServer2(
        host="192.168.1.201",
        qbits=127,
        shots=10000,
        circuit_depth=5000,
        qstorage=(127 * 10000 // 8)
    )
