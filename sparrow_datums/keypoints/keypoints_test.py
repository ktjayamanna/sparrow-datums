import doctest

import numpy as np
import pytest

from sparrow_datums.exceptions import ValidationError
from sparrow_datums.keypoints import keypoints

# from sparrow_datums.keypoints.heatmaps import Heatmaps
from sparrow_datums.keypoints.keypoints import Keypoints
from sparrow_datums.types import PType


def test_docstring_example():
    result = doctest.testmod(keypoints)
    assert result.attempted > 0
    assert result.failed == 0


def test_bad_shape_throws_type_error():
    with pytest.raises(ValidationError):
        Keypoints(np.ones(4))


def test_to_relative_moves_keypoints_to_0_1():
    image_size = 512
    keypoints_a = Keypoints(
        np.random.uniform(size=(10, 2)) * image_size,
        PType.absolute_xy,
        image_width=image_size,
        image_height=image_size,
    )
    keypoints_b = keypoints_a.to_relative()
    assert keypoints_b.is_relative
    np.testing.assert_array_less(keypoints_b.array, 1.0)
    keypoints_c = keypoints_b.to_relative()
    assert keypoints_c.is_relative


def test_to_absolute_moves_keypoints_to_0_image_size():
    image_size = 512
    keypoints_a = Keypoints(
        np.random.uniform(size=(10, 2)),
        PType.relative_xy,
        image_width=image_size,
        image_height=image_size,
    )
    keypoints_b = keypoints_a.to_absolute()
    assert keypoints_b.is_absolute
    assert (keypoints_b.array < 1).mean() < 0.1
    keypoints_c = keypoints_b.to_absolute()
    assert keypoints_c.is_absolute


def test_keypoint_slicing_cols_throws_value_error():
    keypoints = Keypoints(np.random.uniform(size=(10, 2)))
    with pytest.raises(ValidationError):
        keypoints[:, :1]
    top_left = keypoints.array[:, :1]
    assert isinstance(top_left, np.ndarray)


def test_keypoints_deserializes_type():
    keypoints = Keypoints.from_dict(
        {
            "data": [0.2, 0.3],
            "ptype": "relative_xy",
            "image_width": None,
            "image_height": None,
            "fps": None,
            "object_ids": None,
        }
    )
    assert keypoints.ptype == PType.relative_xy


def test_keypoints_saves_classname():
    data = Keypoints(np.ones(2)).to_dict()
    assert data["classname"] == "Keypoints"


def test_keypoint_attributes_require_known_keypoint_parameterization():
    with pytest.raises(ValidationError):
        Keypoints(np.ones(2)).x


# def test_creating_heatmap():
#     image_size = 512
#     keypoints = Keypoints(
#         np.random.uniform(size=(10, 2)),
#         PType.relative_xy,
#         image_width=image_size,
#         image_height=image_size,
#     )
#     heatmaps_array = keypoints.to_heatmap_array()
#     assert heatmaps_array.shape == (10, image_size, image_size)  # check the shape
#     assert type(heatmaps_array) is np.ndarray
#     assert np.min(heatmaps_array) == 0
#     assert np.max(heatmaps_array) == 1
#     heatmaps = Heatmaps(data=heatmaps_array, ptype=PType.heatmap)
#     assert type(heatmaps) is Heatmaps
#     # change the co-variance
#     heatmaps_array = keypoints.to_heatmap_array(covariance=10)
#     np.testing.assert_array_less(heatmaps_array, 1.0000001)


def test_back_and_forth_between_keypoints_and_heatmaps_for_1D_arrays():
    keypoint = Keypoints(
        np.array([4, 8]),
        PType.absolute_xy,
        image_height=21,
        image_width=28,
    )
    heatmap_array = keypoint.to_heatmap_array()
    assert heatmap_array.shape == (keypoint.image_height, keypoint.image_width)
    assert np.max(heatmap_array) == 1
    assert np.min(heatmap_array) == 0
    back_to_keypoint = Keypoints.from_heatmap_array(heatmaps=heatmap_array)
    assert back_to_keypoint[0][0] == keypoint.array[0]
    assert back_to_keypoint[0][1] == keypoint.array[1]
    # assert type(back_to_keypoint) is Keypoints
    # back_to_keypoint_abs = back_to_keypoint.to_absolute()
    # assert back_to_keypoint_abs.is_absolute
    # assert back_to_keypoint_abs[0][0] == keypoint.array[0] * keypoint.image_width
    # assert back_to_keypoint_abs[0][1] == keypoint.array[1] * keypoint.image_height
    # back_to_keypoint_rel = back_to_keypoint.to_relative()
    # assert back_to_keypoint_rel.is_relative


# def test_back_and_forth_between_keypoints_and_heatmaps_for_dense_arrays():
#     n_keypoints = 11
#     np.random.seed(0)
#     candidate_arr = np.random.randint(low=2, high=20, size=(n_keypoints, 2))
#     keypoint = Keypoints(
#         candidate_arr,
#         PType.absolute_kp,
#         image_height=21,
#         image_width=28,
#     )
#     heatmap_array = keypoint.to_heatmap_array()
#     assert heatmap_array.shape == (
#         n_keypoints,
#         keypoint.image_height,
#         keypoint.image_width,
#     )
#     heatmap = Heatmaps(
#         heatmap_array,
#         PType.heatmap,
#         image_width=heatmap_array.shape[-1],
#         image_height=heatmap_array.shape[-2],
#     )
#     assert heatmap.is_heatmap
#     assert heatmap.shape == (n_keypoints, keypoint.image_height, keypoint.image_width)
#     assert np.max(heatmap.array) == 1
#     assert np.min(heatmap.array) == 0
#     back_to_keypoint = heatmap.to_keypoint()
#     assert type(back_to_keypoint) is Keypoints
#     assert back_to_keypoint[7][0] == keypoint.array[7][0]
#     assert back_to_keypoint[7][1] == keypoint.array[7][1]
#     back_to_keypoint_abs = back_to_keypoint.to_absolute()
#     assert back_to_keypoint_abs.is_absolute
#     assert back_to_keypoint_abs[7][0] == keypoint.array[7][0] * keypoint.image_width
#     assert back_to_keypoint_abs[7][1] == keypoint.array[7][1] * keypoint.image_height
#     back_to_keypoint_rel = back_to_keypoint.to_relative()
#     assert back_to_keypoint_rel.is_relative
