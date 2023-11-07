
python3 FTR_inference_video.py --path ckpt/0716_ZITS_video_YoutubeVOS_max750k_mix458k_turn470k_frame-1_1_ReFFC_removed_last --input ./datasets/DAVIS_small/test_set_1/edge_25percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0716_ZITS_video_YoutubeVOS_max750k_mix458k_turn470k_frame-1_1_ReFFC_removed_last --input ./datasets/DAVIS_small/test_set_1/edge_50percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0716_ZITS_video_YoutubeVOS_max750k_mix458k_turn470k_frame-1_1_ReFFC_removed_last --input ./datasets/DAVIS_small/test_set_1/edge_75percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0716_ZITS_video_YoutubeVOS_max750k_mix458k_turn470k_frame-1_1_ReFFC_removed_last --input ./datasets/DAVIS_small/test_set_1/edge_100percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0716_ZITS_video_YoutubeVOS_max750k_mix458k_turn470k_frame-1_1_ReFFC_removed_last --input ./datasets/DAVIS_small/test_set_1/line_25percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0716_ZITS_video_YoutubeVOS_max750k_mix458k_turn470k_frame-1_1_ReFFC_removed_last --input ./datasets/DAVIS_small/test_set_1/line_50percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0716_ZITS_video_YoutubeVOS_max750k_mix458k_turn470k_frame-1_1_ReFFC_removed_last --input ./datasets/DAVIS_small/test_set_1/line_75percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0716_ZITS_video_YoutubeVOS_max750k_mix458k_turn470k_frame-1_1_ReFFC_removed_last --input ./datasets/DAVIS_small/test_set_1/line_100percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 compute_score_summarize.py --root results/0716_ZITS_video_YoutubeVOS_max750k_mix458k_turn470k_frame-1_1_ReFFC_removed_last/Final_result_thesis/DAVIS_test_set1_500k/ --use_DAVIS --cuda --date 2023-09-21

python3 FTR_inference_video.py --path ckpt/0717_ZITS_video_YoutubeVOS_max500k_mix458k_turn470k_prev_and_fixModelForward749 --input ./datasets/DAVIS_small/test_set_1/edge_25percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0717_ZITS_video_YoutubeVOS_max500k_mix458k_turn470k_prev_and_fixModelForward749 --input ./datasets/DAVIS_small/test_set_1/edge_50percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0717_ZITS_video_YoutubeVOS_max500k_mix458k_turn470k_prev_and_fixModelForward749 --input ./datasets/DAVIS_small/test_set_1/edge_75percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0717_ZITS_video_YoutubeVOS_max500k_mix458k_turn470k_prev_and_fixModelForward749 --input ./datasets/DAVIS_small/test_set_1/edge_100percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0717_ZITS_video_YoutubeVOS_max500k_mix458k_turn470k_prev_and_fixModelForward749 --input ./datasets/DAVIS_small/test_set_1/line_25percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0717_ZITS_video_YoutubeVOS_max500k_mix458k_turn470k_prev_and_fixModelForward749 --input ./datasets/DAVIS_small/test_set_1/line_50percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0717_ZITS_video_YoutubeVOS_max500k_mix458k_turn470k_prev_and_fixModelForward749 --input ./datasets/DAVIS_small/test_set_1/line_75percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 FTR_inference_video.py --path ckpt/0717_ZITS_video_YoutubeVOS_max500k_mix458k_turn470k_prev_and_fixModelForward749 --input ./datasets/DAVIS_small/test_set_1/line_100percent --output Final_result_thesis/DAVIS_test_set1_500k
python3 compute_score_summarize.py --root results/0717_ZITS_video_YoutubeVOS_max500k_mix458k_turn470k_prev_and_fixModelForward749/Final_result_thesis/DAVIS_test_set1_500k/ --use_DAVIS --cuda --date 2023-09-21