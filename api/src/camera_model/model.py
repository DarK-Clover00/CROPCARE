import torch
from torch import nn
from torchvision.models import resnet18, ResNet18_Weights

class CropNet(nn.Module):
    """Joint crop/disease categories; crop marginals select disease candidates."""
    def __init__(self, classes, pretrained=False):
        super().__init__()
        self.net = resnet18(weights=ResNet18_Weights.DEFAULT if pretrained else None)
        self.net.fc = nn.Linear(512, len(classes))
    def features(self, x):
        n = self.net
        x = n.maxpool(n.relu(n.bn1(n.conv1(x))))
        x = n.layer4(n.layer3(n.layer2(n.layer1(x))))
        return x
    def forward(self, x, embeddings=False):
        f = self.features(x)
        z = self.net.avgpool(f).flatten(1)
        logits = self.net.fc(z)
        return (logits, z) if embeddings else logits

def load_model(path, device='cpu'):
    ck = torch.load(path, map_location=device, weights_only=True)
    if ck.get('trained_epochs', 0) < 1 or 'calibration' not in ck:
        raise ValueError('Checkpoint is not trained and calibrated')
    model = CropNet(ck['classes']).to(device)
    model.load_state_dict(ck['state'])
    model.eval()
    return model, ck
