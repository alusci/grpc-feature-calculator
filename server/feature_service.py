from concurrent import futures
import grpc
import feature_pb2
import feature_pb2_grpc

from feature_logic import get_cached_features, compute_request_features

class FeatureService(feature_pb2_grpc.FeatureServiceServicer):
    def GetFeatures(self, request, context):
        features = {}
        features.update(get_cached_features(request.user_id))
        features.update(compute_request_features(request.ip_address))
        return feature_pb2.FeatureResponse(features=features)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    feature_pb2_grpc.add_FeatureServiceServicer_to_server(FeatureService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC Feature Service running on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
