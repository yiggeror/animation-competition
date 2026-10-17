"""Real-image registration tests; no network, generator, production writes or large media."""
import importlib.util
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
class PilotMeasurementTests(unittest.TestCase):
    def module(self):
        script = HERE / 'measure_pilot.py'
        self.assertTrue(script.is_file(), 'Fixed two-point measurement script is not implemented yet')
        spec = importlib.util.spec_from_file_location('measure_pilot', script)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        return mod
    def images(self):
        return Image.open(HERE.parent/'refs/x29_look_a.png').convert('RGBA')
    def test_two_point_fit_recovers_known_similarity(self):
        m = self.module(); src = np.array([[1.,2.],[9.,4.]])
        theta=.03; sc=1.01; rot=sc*np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
        dst=src@rot.T+np.array([4.,-6.]); fit=m.solve_two_point_similarity(src,dst)
        np.testing.assert_allclose(m.apply_similarity(src,fit),dst,atol=1e-10)
        np.testing.assert_allclose(fit[:,:2],rot,atol=1e-10)
    def test_fit_rejects_third_input_point_and_degenerate_pair(self):
        m=self.module()
        with self.assertRaises(ValueError):m.solve_two_point_similarity([[0,0],[1,1],[2,2]],[[0,0],[1,1],[2,2]])
        with self.assertRaises(ValueError):m.solve_two_point_similarity([[0,0],[0,0]],[[0,0],[1,1]])
    def test_native_master_self_check(self):
        m=self.module(); im=self.images(); result=m.measure_images(im,im,m.load_config())
        self.assertEqual(result['numeric_failures'],[])
        self.assertLess(result['independent_H_residual_px'],.05)
        self.assertGreater(min(x['ncc'] for x in result['matches'].values()),.999)
        self.assertEqual(result['acceptance'],'manual_structure_and_midpose_review_required')
    def test_global_translation_is_recovered_from_only_A_B(self):
        m=self.module(); im=self.images(); candidate=Image.new('RGBA',im.size);candidate.paste(im,(7,-5))
        result=m.measure_images(im,candidate,m.load_config())
        self.assertEqual(result['numeric_failures'],[])
        np.testing.assert_allclose(np.array(result['candidate_to_master'])[:,2],[-7,5],atol=.15)
        self.assertLess(result['independent_H_residual_px'],.15)
    def test_H_local_drift_is_not_used_to_improve_fit(self):
        m=self.module(); im=self.images(); candidate=im.copy(); box=(405,1240,529,1365)
        part=im.crop(box);candidate.paste((0,0,0,0),box);candidate.paste(part,(box[0]+8,box[1]))
        result=m.measure_images(im,candidate,m.load_config())
        np.testing.assert_allclose(result['candidate_to_master'],[[1,0,0],[0,1,0]],atol=.2)
        self.assertGreater(result['independent_H_residual_px'],5)
        self.assertIn('H_residual_above_3px',result['numeric_failures'])
    def test_hidden_RGB_is_ignored(self):
        m=self.module();im=self.images(); arr=np.array(im);arr[arr[:,:,3]==0,:3]=[255,0,255];candidate=Image.fromarray(arr)
        result=m.measure_images(im,candidate,m.load_config())
        self.assertEqual(result['numeric_failures'],[])
        self.assertLess(result['non_target_registered']['premultiplied_rgb_mae_255'],.02)
    def test_wrong_canvas_fails_without_resizing(self):
        m=self.module();im=self.images();r=m.measure_images(im,im.resize((512,768)),m.load_config())
        self.assertIn('canvas_must_be_1024x1536',r['numeric_failures'])
        self.assertIsNone(r['candidate_to_master'])
    def test_opaque_background_is_rejected(self):
        m=self.module();im=self.images();candidate=im.copy();candidate.putalpha(255)
        r=m.measure_images(im,candidate,m.load_config());self.assertIn('missing_transparent_background',r['numeric_failures'])
    def test_far_translation_is_not_silently_searched_globally(self):
        m=self.module();im=self.images();candidate=Image.new('RGBA',im.size);candidate.paste(im,(70,0))
        r=m.measure_images(im,candidate,m.load_config());self.assertTrue(r['numeric_failures'])
    def test_RGB_image_is_not_accepted_as_alpha_preserved(self):
        m=self.module();im=self.images();r=m.measure_images(im,im.convert('RGB'),m.load_config())
        self.assertIn('RGBA_required',r['numeric_failures'])

if __name__=='__main__':unittest.main()
