#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-05-30 23:55:27
# Project: mit

#bug处理
#1，nav_name为空，抓到一个空首页导航，content也为空,已解决
#2，获取最后一个a标签导致内嵌列表也获取最后一个a标签，修改为if判断text内容，已解决
#3，演讲笔记获取为空，原因是标签（已修复）
#4，视频获取为空，原因也是标签，course_inner_media_gallery,course_inner_media

#创新架构
#1，可以把数据用save传递，等下试试download效果,合并到一起，用一个数组代表nav，然后每个数组元素是一个字典，字典里有名字，内容

from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }

    #@every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://ocw.mit.edu/courses/',callback=self.get_course_list,validate_cert=False)
        #self.crawl('https://ocw.mit.edu/courses/', callback=self.index_page,validate_cert=False)
    
    def get_course_list(self,response):
        for each in response.doc('.oddRow h4 > a').items():
            self.crawl(each.attr.href,callback=self.course_detail_page,validate_cert=False)
        
        for each in response.doc('.evenRow h4 > a').items():
            self.crawl(each.attr.href,callback=self.course_detail_page,validate_cert=False)
    
    def course_detail_page(self,response):
        
        course_info={
            "url":response.url,
            "title":response.doc('h1').text().strip(),
            "img":response.doc('.image > img').attr.src,
            "img_info":response.doc('.caption p').text(),
            "instructor":response.doc('[itemprop="author"]').text(),
            "number":response.doc("#course_info h3:nth-of-type(2)+p").text(),
            "time":response.doc('[itemprop="startDate"]').text(),
            "level":response.doc('[itemprop="typicalAgeRange"]').text(),
            "description":response.doc('#course_tabs [itemprop="description"]').html(),
            "versions":response.doc('#versions > div').html(),
            "related":response.doc('#related > div').html()
        }
        
        #response.doc('#course_nav > ul li:last-child a').remove()
        #response.doc('#course_nav > ul li:first-child a').remove()
        
        for each in response.doc('#course_nav > ul a').items():

            nav_name=each.text().strip()

            if not nav_name:
                continue
            
            if nav_name=="Course Home" or nav_name== "Resource Home":
                continue
            
            if nav_name=="Download Course Materials" or nav_name=="Download Resource Materials":
                self.crawl(each.attr.href,callback=self.course_download,validate_cert=False,save=course_info)
                continue


            course_nav_list={
                "number":course_info["number"],
                "title":course_info["title"],
                "nav_name":nav_name
            }
            self.crawl(each.attr.href,callback=self.course_nav_detail,validate_cert=False,save=course_nav_list)   
        
        return course_info
    
    def course_nav_detail(self,response):
        
        nav_detail_data={
            "number":response.save["number"],
            "title":response.save["title"],
            "nav_name":response.save["nav_name"],
            "content":response.doc('#course_inner_section').html() or response.doc('#course_inner_media_gallery').html() or response.doc('#course_inner_media').html()
            }

        return nav_detail_data
    
    def course_download(self,response):
        #response.save["download"]=response.doc('.downloadNowButton').attr.href
        return {
            "number":response.save["number"],
            "title":response.save["title"],
            "download":response.doc('.downloadNowButton').attr.href
        }
        
    
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            self.crawl(each.attr.href, callback=self.detail_page,validate_cert=False)

    @config(priority=2)
    def detail_page(self, response):
        return {
            "url": response.url,
            "title": response.doc('title').text(),
        }
    
    def test(self,response):
        return {}
