#pragma once
#ifndef _JUMPVISION_H_
#define _JUMPVISION_H_


#include<opencv2/opencv.hpp>
#include<vector>

// capture screenshot of android device & pull to PC
void Capture(std::string name="1") {
	std::string scmd1 = "adb shell screencap -p /storage/emulated/0/DCIM/" + name + ".png";
	std::string scmd2 = "adb pull /storage/emulated/0/DCIM/" + name + ".png ";
	char cmd1[100];
	strncpy_s(cmd1, scmd1.c_str(), scmd1.length());
	char cmd2[100];
	strncpy_s(cmd2, scmd2.c_str(), scmd2.length());
	system(cmd1);
	system(cmd2);
	Sleep(1500);
}


// simulate pressing time(ms) of screen
void Press(int delay) {
	srand((int)time(0));
	int x = rand() % 200 + 600;
	int y = rand() % 201 + 1000;
	std::string scmd = "adb shell input swipe ";
	std::string str;
	std::stringstream ss;
	ss << x;
	ss >> str;
	ss.clear();
	scmd = scmd + str + " ";
	ss << y;
	ss >> str;
	ss.clear();
	scmd = scmd + str + " ";
	ss << (x+10);
	ss >> str;
	ss.clear();
	scmd = scmd + str + " ";
	ss << (y+10);
	ss >> str;
	ss.clear();
	scmd = scmd + str + " ";
	ss << delay;
	ss >> str;
	ss.clear();
	scmd = scmd + str + " ";
	char cmd[100];
//	std::cout << scmd << std::endl;
	strncpy_s(cmd, scmd.c_str(), scmd.length());
	system(cmd);
}


// draw a line on img
void DrawLines(cv::Mat img, double rho, double theta, int B, int G, int R, int thickness,cv::Point ref=cv::Point(0,0))
{
	cv::Point pt1;
	cv::Point pt2;
	pt1.x = cvRound(cos(theta)*rho + 1000 * (-sin(theta)));
	pt1.y = cvRound(sin(theta)*rho + 1000 * (cos(theta)));
	pt2.x = cvRound(cos(theta)*rho - 1000 * (-sin(theta)));
	pt2.y = cvRound(sin(theta)*rho - 1000 * (cos(theta)));
	pt1 += ref;
	pt2 += ref;
	cv::line(img, pt1, pt2, cv::Scalar(B, G, R), 1, CV_AA);
}


// get the intersection of 2 lines
void GetIntersection(double rho1, double theta1, double rho2, double theta2, int& x, int& y)
{
	x = cvRound((rho1*sin(theta2) - rho2 * sin(theta1)) / sin(theta2 - theta1));
	y = cvRound((rho1*cos(theta2) - rho2 * cos(theta1)) / sin(theta1 - theta2));
}


// use TM to match ChessPiece
void MatchUnit(cv::Mat& SrcImg,int& x,int& y) {
	const int ctrx = 38;
	const int ctry = 189;
	cv::Mat UnitImg;
	cv::Mat UnitMatch;
	UnitImg = cv::imread("unit.jpg");
	cv::matchTemplate(SrcImg, UnitImg, UnitMatch, cv::TM_SQDIFF_NORMED);
	double minVal, maxVal;
	cv::Point minPt, maxPt;
	cv::minMaxLoc(UnitMatch, &minVal, &maxVal, &minPt, &maxPt);
	x = minPt.x + ctrx;
	y = minPt.y + ctry;
}


// match the white-dot of aim block
bool MatchAim_Dot(cv::Mat& SrcImg,cv::Mat& RoiCanny, cv::Rect& roirect,int& x,int& y) {
	const double th_match = 0.2;
	const int ctrx = 19;
	const int ctry = 11;
	const int th_pixeloffset = 5;		// pixel offset of (TM & cannyTM)
	cv::Mat RoiImg;
	cv::Mat DotImg;
	cv::Mat DotCanny;
	cv::Mat DotMatch;
	cv::Mat CannyMatch;
	DotImg = cv::imread("dot.jpg");
	SrcImg(roirect).copyTo(RoiImg);
	cv::matchTemplate(RoiImg, DotImg, DotMatch, cv::TM_SQDIFF_NORMED);
	double minVal, maxVal;
	cv::Point minPt, maxPt;
	cv::minMaxLoc(DotMatch, &minVal, &maxVal, &minPt, &maxPt);
//	cv::line(SrcImg, minPt, cv::Point(0, 0), cv::Scalar(255, 255, 0), 1, CV_AA);
	if (minVal < th_match) {
		x = minPt.x + ctrx;
		y = minPt.y + ctry;
		cv::Canny(DotImg, DotCanny, 15, 30);
		cv::matchTemplate(RoiCanny, DotCanny, CannyMatch, cv::TM_SQDIFF_NORMED);
		cv::minMaxLoc(CannyMatch, &minVal, &maxVal, &minPt, &maxPt);
//		cv::namedWindow("11");
//		cv::imshow("11", RoiCanny);
//		cv::waitKey(0);
		if ((abs(minPt.x - x + ctrx)<th_pixeloffset) && (abs(minPt.y - y + ctry)<th_pixeloffset)) {
			std::cout << "Dot matched" << std::endl;
			x += roirect.x;
			y += roirect.y;
			return true;
		}
		else {
			std::cout << "Dot_canny dismatched: " << minVal << std::endl;
		}
	}
//	std::cout << "Dot Dismatched" << std::endl;
	return false;
}


// match aim square block
bool MatchAim_Square(cv::Mat& SrcImg,cv::Mat& RoiCanny, cv::Rect& roirect,int& x,int& y,int xBeg,int yBeg) {
	const int th_hough = 100;
	const int th_interval = 100;
	const int th_differential = 3;
	const int th_movement = 50;
	const double theta_uldr = 2.095;
	const double theta_urdl = 1.045;
	std::vector<cv::Vec2f> Lines;
	std::vector<double> ul_dr;		// theta ~= 2.095
	std::vector<double> ur_dl;		// theta ~= 1.045
	cv::HoughLines(RoiCanny, Lines, 1, CV_PI / 180, th_hough);
	for (size_t i = 0; i < Lines.size(); ++i) {
		if (abs(Lines[i][1] - theta_urdl) < 0.005) {
			ur_dl.push_back(Lines[i][0]);
			//DrawLines(SrcImg, Lines[i][0], Lines[i][1], 0, 255, 0, 1);
		}
		if (abs(Lines[i][1] - theta_uldr) < 0.005) {
			ul_dr.push_back(Lines[i][0]);
			//DrawLines(SrcImg, Lines[i][0], Lines[i][1], 0, 255, 0, 1);
		}
	}
	if (ul_dr.size() < 2 || ur_dl.size() < 2) {
		std::cout << "Square dismatched : not enough lines" << std::endl;
		return false;
	}
	std::sort(ul_dr.begin(), ul_dr.end());
	std::sort(ur_dl.begin(), ur_dl.end());
	double dist;
	for (size_t i1 = 0; i1 < ul_dr.size() - 1; ++i1) {
		for (size_t i2 = i1 + 1; i2 < ul_dr.size(); ++i2) {
			dist = ul_dr.at(i2) - ul_dr.at(i1);
			if (dist < th_interval) {
				continue;
			}
			for (size_t j1 = 0; j1 < ur_dl.size(); ++j1) {
				for (size_t j2 = j1+1; j2 < ur_dl.size(); ++j2) {
					if (abs(ur_dl.at(j2) - ur_dl.at(j1) - dist) < th_differential) {
						GetIntersection((ul_dr.at(i2) + ul_dr.at(i1)) / 2, theta_uldr, (ur_dl.at(j2) + ur_dl.at(j1)) / 2, theta_urdl, x, y);

						/*
						cv::line(SrcImg, cv::Point(0, 0), cv::Point(x+roirect.x, y+roirect.y), 255, 0, 255, 1);

						DrawLines(SrcImg, (ul_dr.at(i2) + ul_dr.at(i1)) / 2, theta_uldr, 0, 0, 255, 1, cv::Point(roirect.x, roirect.y));
						DrawLines(SrcImg, (ur_dl.at(j2) + ur_dl.at(j1)) / 2, theta_urdl, 0, 0, 255, 1, cv::Point(roirect.x, roirect.y));


						DrawLines(SrcImg, ul_dr.at(i1), theta_uldr, 0, 0, 255, 1, cv::Point(roirect.x, roirect.y));
						DrawLines(SrcImg, ul_dr.at(i2), theta_uldr, 0, 0, 255, 1, cv::Point(roirect.x, roirect.y));
						DrawLines(SrcImg, ur_dl.at(j1), theta_urdl, 0, 0, 255, 1, cv::Point(roirect.x, roirect.y));
						DrawLines(SrcImg, ur_dl.at(j2), theta_urdl, 0, 0, 255, 1, cv::Point(roirect.x, roirect.y));
						cv::namedWindow("11");
						cv::imshow("11", SrcImg);
						cv::waitKey(0);

*/
						x += roirect.x;
						y += roirect.y;
						if (abs(x - xBeg) < th_movement || yBeg - y < th_movement) {
							continue;
						}
						else {
							std::cout << "Square matched" << std::endl;
							return true;
						}
					}
				}
			}
		}
	}
	std::cout << "Square dismatched : cannot find appropriate lines" << std::endl;
	return false;
}



bool MatchAim_Circle(cv::Mat& SrcImg,cv::Rect& roirect,int& x,int& y) {
	std::cout << "matching circle" << std::endl;
	const double resize_ratio = 451.0 / 262.0;
	cv::Mat gRoiImg;
	cv::Mat RoiImg;
	cv::Mat RoiImg_resize;
	SrcImg(roirect).copyTo(RoiImg);
	cv::resize(RoiImg, RoiImg_resize, cv::Size(roirect.width, cvRound(roirect.height*resize_ratio)));
	cv::cvtColor(RoiImg_resize, gRoiImg, cv::COLOR_BGR2GRAY);
	std::vector<cv::Vec3f> Circles;
	cv::HoughCircles(gRoiImg, Circles, CV_HOUGH_GRADIENT, 1, 50, 30, 30,5,500);
	for (size_t i = 0; i < Circles.size(); ++i) {
		cv::Point center(cvRound(Circles[i][0]), cvRound(Circles[i][1]));
		int radius = cvRound(Circles[i][2]);
		cv::circle(gRoiImg, center, radius, 0, 1);
	}
	if (Circles.size() == 1) {
		x = cvRound(Circles[0][0]) + roirect.x;
		y = cvRound(Circles[0][1] / resize_ratio) + roirect.y;
		return true;
	}
	else {
		system("pause");
	}








	cv::namedWindow("11");
	cv::imshow("11", gRoiImg);
	cv::waitKey(0);






	return false;
}


// get center of circle in ROI in an ugly way :(
void MatchAim_Circle_ugly(cv::Mat& RoiCanny,cv::Rect& roirect, int& x, int& y) {
	std::cout << "ugly match" << std::endl;
	cv::Mat cache(RoiCanny);


	/*
	cv::namedWindow("aa");
	cv::imshow("aa", RoiCanny);
	cv::waitKey(0);
*/

	int yup, ydn, xct;
	for (int j = 100; j < cache.rows; ++j) {
		for (int i = 100; i < cache.cols-100; ++i) {
			if (cache.at<uchar>(j, i) != 0) {
				xct = i;
				yup = j;
				int k;
				for (k = yup + 5; k < cache.rows; ++k) {
					if (cache.at<uchar>(k,xct) != 0) {
						break;
					}
				}
				ydn = k;
				x = xct + roirect.x;
				y = (yup + ydn) / 2 + roirect.y;
				return;
			}
		}
	}
}














void MatchAim(cv::Mat& SrcImg, int& x, int& y,int xBeg,int yBeg) {
	// canny & set ROI
	cv::Mat CannyImg;
	cv::Mat RoiCanny;
	cv::Canny(SrcImg, CannyImg, 15, 30);
	const int roiw = 300;
	const int roih = 300;
	int roix;
	int roiy;
	roix = ((1080 - xBeg - roiw > 2) ? (1080 - xBeg - roiw) : 2);
	roiy = 1920 - yBeg - roih;
	cv::Rect roirect(cv::Point(roix, roiy), cv::Point(((1080 - xBeg + roiw < 1078) ? (1080 - xBeg + roiw) : 1078), roiy + 2 * roih));
	CannyImg(roirect).copyTo(RoiCanny);
	cv::imwrite("RoiCanny.png", RoiCanny);
	/*
	cv::Mat aa;
	aa = cv::imread("square.jpg", CV_LOAD_IMAGE_ANYDEPTH);
	cv::Mat bb;
	double minVal, maxVal;
	cv::Point minPt, maxPt;
	cv::matchTemplate(CannyImg, aa, bb, cv::TM_SQDIFF_NORMED);
	cv::minMaxLoc(bb, &minVal, &maxVal, &minPt, &maxPt);
	std::cout << minVal << std::endl;
	x = minPt.x + 226;
	y = minPt.y + 131;
*/

	if (MatchAim_Dot(SrcImg,RoiCanny,roirect, x, y)) {
		return;
	}
	/*
	else if (MatchAim_Square(SrcImg,RoiCanny,roirect, x, y, xBeg, yBeg)) {
		return;
	}*/
	else {
//		MatchAim_Circle(SrcImg, roirect, x, y);
		for (int i = xBeg - 50; i < xBeg + 50; ++i) {
			for (int j = yBeg - 250; j < yBeg + 22; ++j) {
				CannyImg.at<uchar>(j, i) = 0;
			}
		}
		CannyImg(roirect).copyTo(RoiCanny);
		MatchAim_Circle_ugly(RoiCanny, roirect, x, y);
	}
}





// read image - calculate distance - press simulation
bool Process() {
	std::cout << "process" << std::endl;
	const double jump_ratio=1.452;

	Capture();	
	
	cv::Mat SrcImg;
	cv::Mat EndImg;
	cv::Mat EndMatch;
	SrcImg = cv::imread("1.png");
	EndImg = cv::imread("end.jpg");

	cv::matchTemplate(SrcImg, EndImg, EndMatch, cv::TM_SQDIFF_NORMED);
	double minVal, maxVal;
	cv::Point minPt, maxPt;
	cv::minMaxLoc(EndMatch, &minVal, &maxVal, &minPt, &maxPt);
	if (minVal < 0.1) {
		return false;
	}

	//cv::imwrite("SrcImg.png", SrcImg);


	int xBeg, yBeg;
	MatchUnit(SrcImg, xBeg, yBeg);
	int xAim, yAim;
	MatchAim(SrcImg, xAim, yAim, xBeg, yBeg);


	int dist;
	dist = cvRound(sqrt((xAim - xBeg)*(xAim - xBeg) + (yAim - yBeg)*(yAim - yBeg)));
	std::cout << "start:" << xBeg << "," << yBeg << " towards:" << xAim << "," << yAim << " distance: " << dist << std::endl;
	//Press(750);
	//RoiImg(cv::Rect(cv::Point(119, 208), cv::Point(570, 470))).copyTo(aa);
	//cv::imwrite("square.jpg", aa);



	// display

	/*
	cv::line(SrcImg, cv::Point(1080 - xBeg + roiw, 1920 - yBeg + roih), cv::Point(1080 - xBeg + roiw, 1920 - yBeg - roih), cv::Scalar(0, 0, 255), 1, CV_AA);
	cv::line(SrcImg, cv::Point(1080 - xBeg - roiw, 1920 - yBeg - roih), cv::Point(1080 - xBeg + roiw, 1920 - yBeg - roih), cv::Scalar(0, 0, 255), 1, CV_AA);
	cv::line(SrcImg, cv::Point(1080 - xBeg + roiw, 1920 - yBeg + roih), cv::Point(1080 - xBeg - roiw, 1920 - yBeg + roih), cv::Scalar(0, 0, 255), 1, CV_AA);
	cv::line(SrcImg, cv::Point(1080 - xBeg - roiw, 1920 - yBeg - roih), cv::Point(1080 - xBeg - roiw, 1920 - yBeg + roih), cv::Scalar(0, 0, 255), 1, CV_AA);
*/
	cv::line(SrcImg, cv::Point(xBeg,yBeg), cv::Point(0, 0), cv::Scalar(255, 0, 0), 1, CV_AA);
	//cv::line(SrcImg, cv::Point(xAim, yAim), cv::Point(0, 0), cv::Scalar(255, 0, 0), 1, CV_AA);
	/*
	cv::namedWindow("aa");
	cv::Mat showImg;
	cv::resize(SrcImg, showImg, cv::Size(540, 960));
	cv::imshow("aa", showImg);
	cv::waitKey(0);
	cv::destroyWindow("aa");
	system("pause");
	*/
	Press(int(dist*jump_ratio));
	Sleep(1500);


	return true;
}












#endif // !_JUMPVISION_H_
