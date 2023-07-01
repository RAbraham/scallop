from typing import List, Tuple

from .torch_importer import *

from .scallopy import InternalScallopCollection

class ScallopCollection:
  def __init__(
    self,
    provenance: str,
    internal_collection: InternalScallopCollection,
  ):
    self.provenance = provenance
    self._internal = internal_collection

  def __iter__(self):
    if self.provenance == "diffminmaxprob":
      for ((s, p), t) in self._internal:
        if s == 1:
          yield (p, t)
        elif s == 0:
          yield (torch.tensor(p), t)
        else:
          yield (1 - p, t)
    elif self.provenance == "diffaddmultprob" or \
         self.provenance == "diffnandmultprob" or \
         self.provenance == "diffmaxmultprob" or \
         self.provenance == "diffnandminprob" or \
         self.provenance == "difftopkproofs" or \
         self.provenance == "diffsamplekproofs" or \
         self.provenance == "difftopbottomkclauses":
      input_tags = self._internal.input_tags()
      for ((p, deriv), t) in self._internal:
        diff_prob = diff_proofs_prob(p, deriv, input_tags)
        yield (diff_prob, t)
    else:
      for t in self._internal:
        yield t

def diff_proofs_prob(p: float, deriv: List[Tuple[int, float, Tensor]], input_tags: List[Tensor]):
  def hook(grad):
    for (tag_id, weight) in deriv:
      source_tensor = input_tags[tag_id]
      if source_tensor.requires_grad:
        source_tensor.backward(weight * grad, retain_graph=True)
  v = torch.tensor(p, requires_grad=True)
  v.register_hook(hook)
  return v
