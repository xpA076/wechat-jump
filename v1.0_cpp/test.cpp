//**********************************************************************//
//                            _ooOoo_									//
//                           o8888888o									//	
//                           88" . "88									//
//                           (| -_- |)									//
//                            O\ = /O									//
//                        ____/`---'\____								//
//                      .   ' \\| |// `.								//
//                       / \\||| : |||// \								//
//                     / _||||| -:- |||||- \							//
//                       | | \\\ - /// | |								//
//                     | \_| ''\---/'' | |								//
//                      \ .-\__ `-` ___/-. /							//
//                   ___`. .' /--.--\ `. . __							//
//                ."" '< `.___\_<|>_/___.' >'"".						//
//               | | : `- \`.;`\ _ /`;.`/ - ` : | |						//
//                 \ \ `-. \_ __\ /__ _/ .-` / /						//
//         ======`-.____`-.___\_____/___.-`____.-'======				//
//                            `=---='									//
//																		//
//         .............................................				//
//                  ���汣��             ����BUG						//
//          ��Ի:														//
//                  д��¥��д�ּ䣬д�ּ������Ա��					//
//                  ������Աд�������ó��򻻾�Ǯ��					//  
//                  ����ֻ�����������������������ߣ�  					//
//                  ���������ո��գ����������긴�ꡣ  					//
//                  ��Ը�������Լ䣬��Ը�Ϲ��ϰ�ǰ��  					//
//                  ���۱�������Ȥ���������г���Ա��  					//
//                  ����Ц��߯��񲣬��Ц�Լ���̫����  					//
//                  ��������Ư���ã��ĸ���ó���Ա��  					//
//																		//
//**********************************************************************//


// debug in win10-VS2017 & MI6(MIUI)


#include<opencv2/opencv.hpp>
#include<iostream>
#include<windows.h>
#include"JumpVision.h"

int main() {
	double jump_ratio = 1.390;
	double input;
	std::cout << "input ratio_factor (or press enter using default:1.390):" << std::endl;
	std::cin>>std::noskipws >> input;
	if (input > 0) {
		jump_ratio = input;
	}
	std::cout << "starting" << std::endl;
	for (int i = 0; i < 500; ++i) {
		if (!Process(jump_ratio)) {
			break;
		}
	}
	std::cout << "end game" << std::endl;
	system("pause");
	return 0;
}