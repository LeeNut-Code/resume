#!/usr/bin/env python3
"""
简历自动更新脚本
当简历Markdown文件变更时，自动更新HTML网页内容
"""

import os
import re
import markdown
from bs4 import BeautifulSoup
import yaml
import datetime

class ResumeUpdater:
    """简历更新器类"""
    
    def __init__(self, resume_path, html_path, config_path=None):
        """
        初始化简历更新器
        
        Args:
            resume_path: 简历Markdown文件路径
            html_path: HTML网页文件路径
            config_path: 配置文件路径
        """
        self.resume_path = resume_path
        self.html_path = html_path
        # 明确配置文件路径
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')
        self.resume_content = ""
        self.html_content = ""
        self.soup = None
        self.config = {}
    
    def load_resume(self):
        """加载并解析简历Markdown文件"""
        try:
            with open(self.resume_path, 'r', encoding='utf-8') as f:
                self.resume_content = f.read()
            print("✓ 成功加载简历文件")
            return True
        except Exception as e:
            print(f"✗ 加载简历文件失败: {e}")
            return False
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print("✓ 成功加载配置文件")
            return True
        except Exception as e:
            print(f"✗ 加载配置文件失败: {e}")
            return False
    
    def update_last_updated(self):
        """更新最后更新时间"""
        try:
            # 更新配置文件中的最后更新时间
            if self.config:
                self.config['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                print("✓ 成功更新最后更新时间")
                return True
            else:
                print("✗ 配置文件未加载，无法更新最后更新时间")
                return False
        except Exception as e:
            print(f"✗ 更新最后更新时间失败: {e}")
            return False
    
    def load_html(self):
        """加载HTML文件"""
        try:
            with open(self.html_path, 'r', encoding='utf-8') as f:
                self.html_content = f.read()
            self.soup = BeautifulSoup(self.html_content, 'html.parser')
            print("✓ 成功加载HTML文件")
            return True
        except Exception as e:
            print(f"✗ 加载HTML文件失败: {e}")
            return False
    
    def extract_personal_info(self):
        """提取个人基本信息"""
        info = {}
        
        # 提取姓名
        name_match = re.search(r'<h1[^>]*>(.*?)</h1>', self.resume_content)
        if name_match:
            info['name'] = name_match.group(1).strip()
        
        # 提取联系方式
        contact_match = re.search(r'> 电话：`(.*?)`&emsp;\|&emsp;邮箱：\[(.*?)\]', self.resume_content)
        if contact_match:
            info['phone'] = contact_match.group(1).strip()
            info['email'] = contact_match.group(2).strip()
        
        # 提取基本信息
        basic_info_match = re.search(r'## 基本信息\n\n(.*?)## 教育背景', self.resume_content, re.DOTALL)
        if basic_info_match:
            basic_info = basic_info_match.group(1).strip()
            
            # 使用更简单的方法提取基本信息
            # 提取性别
            if '性别：' in basic_info:
                gender_part = basic_info.split('性别：')[1].split('&emsp;')[0].strip()
                if gender_part:
                    info['gender'] = gender_part
                else:
                    # 如果性别为空，尝试从下一行提取
                    next_part = basic_info.split('性别：')[1].split('\n')[1].strip()
                    if next_part.startswith('民族：'):
                        # 性别确实为空
                        info['gender'] = '男'  # 默认值，根据实际情况修改
            
            # 提取年龄
            if '年龄：' in basic_info:
                age_part = basic_info.split('年龄：')[1].split('\n')[0].strip()
                if age_part:
                    info['age'] = age_part
            
            # 提取民族
            if '民族：' in basic_info:
                nation_part = basic_info.split('民族：')[1].split('&emsp;')[0].strip()
                if nation_part:
                    info['nation'] = nation_part
            
            # 提取籍贯
            if '籍贯：' in basic_info:
                origin_part = basic_info.split('籍贯：')[1].split('\n')[0].strip()
                if origin_part:
                    # 移除多余的空格
                    origin_part = origin_part.replace('  ', ' ')
                    info['origin'] = origin_part
            
            # 提取学历
            education_match = re.search(r'学历：(.*?)\s+', basic_info)
            if education_match:
                info['education'] = education_match.group(1).strip().replace('**', '')
            
            # 提取网站
            website_match = re.search(r'网站：\s*\[(.*?)\]', basic_info)
            if website_match:
                info['website'] = website_match.group(1).strip()
            
            # 提取Github
            github_match = re.search(r'Github：\s*\[(.*?)\]', basic_info)
            if github_match:
                info['github'] = github_match.group(1).strip()
        
        return info
    
    def update_personal_info(self):
        """更新个人基本信息"""
        info = self.extract_personal_info()
        # 提取教育背景信息
        education_list = self.extract_education()
        
        if not info:
            print("✗ 未提取到个人信息")
            return False
        
        try:
            # 更新姓名
            if 'name' in info:
                name_elem = self.soup.find('h1', class_='text-4xl')
                if name_elem:
                    name_elem.string = info['name']
            
            # 更新联系方式
            contact_elems = self.soup.find_all('div', class_='flex items-center gap-2 text-medium')
            for elem in contact_elems:
                icon = elem.find('i')
                if icon:
                    if 'fa-phone' in icon.get('class', []):
                        span = elem.find('span')
                        if span and 'phone' in info:
                            span.string = info['phone']
                    elif 'fa-envelope' in icon.get('class', []):
                        a = elem.find('a')
                        if a and 'email' in info:
                            a.string = info['email']
                            a['href'] = f'mailto:{info["email"]}'
                    elif 'fa-globe' in icon.get('class', []):
                        a = elem.find('a')
                        if a and 'website' in info:
                            a.string = info['website']
                            a['href'] = f'https://{info["website"]}'
                    elif 'fa-github' in icon.get('class', []):
                        a = elem.find('a')
                        if a and 'github' in info:
                            a.string = info['github'].split('/')[-1] if '/' in info['github'] else info['github']
                            a['href'] = info['github']
            
            # 更新基本信息表格
            info_grid = self.soup.find('div', class_=lambda x: x and 'grid' in x)
            if info_grid:
                # 只查找直接子元素
                info_items = info_grid.find_all('div', recursive=False)
                if len(info_items) >= 2:
                    # 左侧信息
                    left_info = info_items[0]
                    if left_info:
                        # 清空现有 p 元素
                        for p in left_info.find_all('p'):
                            p.decompose()
                        # 根据当前 info 动态创建 p 元素
                        if 'gender' in info:
                            gender_p = self.soup.new_tag('p')
                            gender_p['class'] = ['text-medium', 'mb-1']
                            gender_p.string = f'性别：{info["gender"]}'
                            left_info.append(gender_p)
                        if 'age' in info:
                            age_p = self.soup.new_tag('p')
                            age_p['class'] = ['text-medium', 'mb-1']
                            age_p.string = f'年龄：{info["age"]}'
                            left_info.append(age_p)
                        if 'nation' in info:
                            nation_p = self.soup.new_tag('p')
                            nation_p['class'] = ['text-medium', 'mb-1']
                            nation_p.string = f'民族：{info["nation"]}'
                            left_info.append(nation_p)
                        if 'origin' in info:
                            origin_p = self.soup.new_tag('p')
                            origin_p['class'] = ['text-medium', 'mb-1']
                            origin_p.string = f'籍贯：{info["origin"]}'
                            left_info.append(origin_p)
                    
                    # 右侧信息
                    right_info = info_items[1]
                    # 清空右侧信息的现有内容
                    for p in right_info.find_all('p'):
                        p.decompose()
                    
                    # 从第一段教育背景中获取信息
                    if education_list:
                        first_education = education_list[0]
                        # 添加学历
                        education_level = '本科'  # 默认值
                        school = first_education.get('school', '未知学校')
                        # 尝试从学校名称中提取学历
                        if '（本科）' in school:
                            education_level = '本科'
                        elif '（硕士）' in school:
                            education_level = '硕士研究生'
                        elif '（博士）' in school:
                            education_level = '博士研究生'
                        
                        # 创建学历 p 元素
                        education_p = self.soup.new_tag('p')
                        education_p['class'] = ['text-medium', 'mb-1']
                        education_p.string = f'学历：{education_level}'
                        right_info.append(education_p)
                        
                        # 添加专业
                        major = first_education.get('major', '未知专业')
                        major_p = self.soup.new_tag('p')
                        major_p['class'] = ['text-medium', 'mb-1']
                        major_p.string = f'专业：{major}'
                        right_info.append(major_p)
                        
                        # 添加毕业院校
                        # 从学校名称中移除学历部分
                        if '（' in school and '）' in school:
                            school_name = school.split('（')[0]
                        else:
                            school_name = school
                        school_p = self.soup.new_tag('p')
                        school_p['class'] = ['text-medium', 'mb-1']
                        school_p.string = f'毕业院校：{school_name}'
                        right_info.append(school_p)
            
            print("✓ 成功更新个人信息")
            return True
        except Exception as e:
            print(f"✗ 更新个人信息失败: {e}")
            return False
    
    def extract_education(self):
        """提取教育背景信息"""
        education_list = []
        
        # 提取教育背景
        edu_match = re.search(r'## 教育背景\n\n(.*?)## 实习经历', self.resume_content, re.DOTALL)
        if edu_match:
            edu_content = edu_match.group(1).strip()
            
            # 分割教育背景记录 - 按<div style="display: flex; justify-content: space-between; align-items: center;">分割
            edu_records = edu_content.split('<div style="display: flex; justify-content: space-between; align-items: center;">')
            
            # 跳过第一个空字符串（因为分割后第一个元素是空的）
            for i, record in enumerate(edu_records[1:]):
                if record.strip():
                    # 处理单个教育背景记录
                    education = {}
                    
                    # 提取时间、学校和专业 - 使用更精确的匹配
                    # 匹配格式： <div style="flex: 1; text-align: left;"><b>时间</b></div>
                    # 匹配格式： <div style="flex: 1; text-align: center;"><b>学校</b></div>
                    # 匹配格式： <div style="flex: 1; text-align: right;"><b>专业</b></div>
                    time_match = re.search(r'<div style="flex: 1; text-align: left;"><b>(.*?)</b></div>', record)
                    school_match = re.search(r'<div style="flex: 1; text-align: center;"><b>(.*?)</b></div>', record)
                    major_match = re.search(r'<div style="flex: 1; text-align: right;"><b>(.*?)</b></div>', record)
                    
                    if time_match:
                        education['time'] = time_match.group(1).strip()
                    if school_match:
                        education['school'] = school_match.group(1).strip()
                    if major_match:
                        education['major'] = major_match.group(1).strip()
                    
                    # 提取主修课程
                    # 查找'- 主修课程：'的位置
                    courses_start = record.find('- 主修课程：')
                    if courses_start != -1:
                        # 提取从'- 主修课程：'到下一个<div>或结束的内容
                        next_div = record.find('<div', courses_start)
                        if next_div != -1:
                            courses_content = record[courses_start:next_div].strip()
                        else:
                            courses_content = record[courses_start:].strip()
                        
                        # 移除'- 主修课程：'前缀
                        courses = courses_content.replace('- 主修课程：', '').strip()
                        # 移除可能的HTML转义字符
                        courses = courses.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                        education['courses'] = [course.strip() for course in courses.split('、')]
                    
                    if education:
                        education_list.append(education)
        
        return education_list
    
    def update_education(self):
        """更新教育背景信息"""
        education_list = self.extract_education()
        
        if not education_list:
            print("✗ 未提取到教育背景信息，不加载该部分")
            # 如果没有教育背景，移除网页中的教育背景部分
            edu_section = self.soup.find('section', id='education')
            if edu_section:
                edu_section.decompose()
            # 移除导航栏中的教育背景链接
            nav = self.soup.find('nav')
            if nav:
                edu_link = nav.find('a', href='#education')
                if edu_link:
                    edu_link.decompose()
            # 移除移动端导航栏中的教育背景链接
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                mobile_edu_link = mobile_nav.find('a', href='#education')
                if mobile_edu_link:
                    mobile_edu_link.decompose()
            # 移除教育背景的注释标记
            for comment in self.soup.find_all(text=lambda text: isinstance(text, str) and '<!-- 教育背景 -->' in text):
                comment.extract()
            return True
        
        try:
            # 更新教育背景卡片
            edu_section = self.soup.find('section', id='education')
            if edu_section:
                # 完全清空教育背景部分的内容
                edu_section.clear()
                
                # 创建新的容器
                container = self.soup.new_tag('div')
                container['class'] = ['container', 'mx-auto', 'px-4']
                edu_section.append(container)
                
                # 创建标题
                title_div = self.soup.new_tag('div')
                title_div['class'] = ['text-center', 'mb-12']
                title_h2 = self.soup.new_tag('h2')
                title_h2['class'] = ['text-3xl', 'font-bold', 'mb-2']
                title_h2.string = '教育背景'
                title_div.append(title_h2)
                title_line = self.soup.new_tag('div')
                title_line['class'] = ['w-20', 'h-1', 'bg-primary', 'mx-auto']
                title_div.append(title_line)
                container.append(title_div)
                
                # 创建新的内容容器
                content_container = self.soup.new_tag('div')
                content_container['class'] = ['max-w-4xl', 'mx-auto']
                container.append(content_container)
                
                # 如果有两段教育背景，使用标签栏切换布局
                if len(education_list) == 2:
                    # 创建标签栏容器
                    tab_container = self.soup.new_tag('div')
                    tab_container['class'] = ['mb-8']
                    content_container.append(tab_container)
                    
                    # 创建标签按钮组
                    tab_buttons = self.soup.new_tag('div')
                    tab_buttons['class'] = ['flex', 'justify-center', 'gap-4', 'p-2']
                    tab_container.append(tab_buttons)
                    
                    # 定义多彩颜色
                    colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-pink-500', 'bg-yellow-500', 'bg-orange-500', 'bg-teal-500']
                    
                    # 创建标签按钮
                    tabs = []
                    for i, edu in enumerate(education_list):
                        # 创建标签按钮
                        tab_button = self.soup.new_tag('button')
                        tab_button['id'] = f'tab-education-{i+1}'
                        color_class = colors[i % len(colors)]
                        if i == 0:
                            tab_button['class'] = ['w-16', 'h-16', 'rounded-full', color_class, 'text-white', 'flex', 'items-center', 'justify-center', 'shadow-lg', 'transition-all', 'duration-300', 'transform', 'scale-105', 'focus:outline-none', 'focus:ring-2', f'focus:ring-{color_class.replace("bg-", "")}/20']
                        else:
                            tab_button['class'] = ['w-16', 'h-16', 'rounded-full', color_class, 'text-white', 'flex', 'items-center', 'justify-center', 'shadow-md', f'hover:{color_class}/80', 'transition-all', 'duration-300', 'focus:outline-none', 'focus:ring-2', f'focus:ring-{color_class.replace("bg-", "")}/20']
                        # 添加图标
                        tab_icon = self.soup.new_tag('i')
                        tab_icon['class'] = ['fa', 'fa-graduation-cap', 'text-xl']
                        tab_button.append(tab_icon)
                        tab_buttons.append(tab_button)
                        tabs.append(tab_button)
                    
                    # 创建内容容器
                    content_wrapper = self.soup.new_tag('div')
                    content_wrapper['class'] = ['bg-white', 'rounded-xl', 'shadow-lg', 'overflow-hidden', 'border', 'border-gray-100']
                    content_container.append(content_wrapper)
                    
                    # 创建第一个内容面板
                    panel1 = self.soup.new_tag('div')
                    panel1['id'] = 'panel-education-1'
                    panel1['class'] = ['p-8', 'animate-fade-in']
                    content_wrapper.append(panel1)
                    
                    # 添加学校名称
                    school_name1 = self.soup.new_tag('div')
                    school_name1['class'] = ['font-semibold', 'text-xl', 'flex', 'items-center', 'gap-3', 'mb-4']
                    panel1.append(school_name1)
                    
                    school_icon1 = self.soup.new_tag('i')
                    school_icon1['class'] = ['fa', 'fa-graduation-cap', 'text-primary', 'text-xl']
                    school_name1.append(school_icon1)
                    
                    school_name_span1 = self.soup.new_tag('span')
                    if 'school' in education_list[0]:
                        school_name_span1.string = education_list[0]['school']
                    school_name1.append(school_name_span1)
                    
                    # 添加时间
                    time_elem1 = self.soup.new_tag('div')
                    time_elem1['class'] = ['text-primary', 'font-medium', 'mb-4', 'flex', 'items-center', 'gap-2']
                    time_icon1 = self.soup.new_tag('i')
                    time_icon1['class'] = ['fa', 'fa-calendar', 'text-primary']
                    time_elem1.append(time_icon1)
                    if 'time' in education_list[0]:
                        time_elem1.append(education_list[0]['time'])
                    panel1.append(time_elem1)
                    
                    # 添加专业
                    major_elem1 = self.soup.new_tag('div')
                    major_elem1['class'] = ['text-medium', 'bg-primary/10', 'text-primary', 'px-4', 'py-2', 'rounded-full', 'text-sm', 'mb-6', 'inline-block']
                    if 'major' in education_list[0]:
                        major_elem1.string = education_list[0]['major']
                    panel1.append(major_elem1)
                    
                    # 添加主修课程
                    if 'courses' in education_list[0] and education_list[0]['courses']:
                        course_card1 = self.soup.new_tag('div')
                        course_card1['class'] = ['bg-gradient-to-br', 'from-purple-50', 'to-blue-50', 'rounded-xl', 'p-6', 'shadow-sm', 'mt-6']
                        panel1.append(course_card1)
                        
                        course_title1 = self.soup.new_tag('h3')
                        course_title1['class'] = ['font-medium', 'mb-6', 'flex', 'items-center', 'gap-3', 'text-lg', 'text-gray-800']
                        course_card1.append(course_title1)
                        
                        course_icon1 = self.soup.new_tag('i')
                        course_icon1['class'] = ['fa', 'fa-book', 'text-primary']
                        course_title1.append(course_icon1)
                        
                        course_title_span1 = self.soup.new_tag('span')
                        course_title_span1.string = '主修课程'
                        course_title1.append(course_title_span1)
                        
                        # 创建课程容器
                        course_container1 = self.soup.new_tag('div')
                        course_container1['class'] = ['relative']
                        course_card1.append(course_container1)
                        
                        # 创建课程网格
                        course_grid1 = self.soup.new_tag('div')
                        course_grid1['id'] = 'courses-grid-1'
                        course_grid1['class'] = ['grid', 'grid-cols-1', 'sm:grid-cols-2', 'md:grid-cols-3', 'gap-4', 'max-h-64', 'overflow-hidden', 'transition-all', 'duration-500']
                        course_container1.append(course_grid1)
                        
                        for course in education_list[0]['courses']:
                            course_div1 = self.soup.new_tag('div')
                            course_div1['class'] = ['bg-white', 'px-4', 'py-3', 'rounded-lg', 'text-sm', 'text-medium', 'shadow-sm', 'hover:shadow-md', 'transition-all', 'duration-300', 'transform', 'hover:scale-105', 'border', 'border-gray-100']
                            course_div1.string = course
                            course_grid1.append(course_div1)
                        
                        # 添加展开/收起按钮
                        if len(education_list[0]['courses']) > 8:  # 假设每行显示2-3个课程，4行大约8-12个课程
                            toggle_btn1 = self.soup.new_tag('button')
                            toggle_btn1['id'] = 'toggle-courses-1'
                            toggle_btn1['class'] = ['mt-4', 'text-primary', 'font-medium', 'flex', 'items-center', 'gap-2', 'hover:underline', 'focus:outline-none']
                            toggle_btn1.string = '展开全部'
                            toggle_icon1 = self.soup.new_tag('i')
                            toggle_icon1['class'] = ['fa', 'fa-chevron-down']
                            toggle_btn1.append(toggle_icon1)
                            course_card1.append(toggle_btn1)
                    
                    # 创建第二个内容面板
                    panel2 = self.soup.new_tag('div')
                    panel2['id'] = 'panel-education-2'
                    panel2['class'] = ['p-8', 'hidden', 'animate-fade-in']
                    content_wrapper.append(panel2)
                    
                    # 添加学校名称
                    school_name2 = self.soup.new_tag('div')
                    school_name2['class'] = ['font-semibold', 'text-xl', 'flex', 'items-center', 'gap-3', 'mb-4']
                    panel2.append(school_name2)
                    
                    school_icon2 = self.soup.new_tag('i')
                    school_icon2['class'] = ['fa', 'fa-graduation-cap', 'text-primary', 'text-xl']
                    school_name2.append(school_icon2)
                    
                    school_name_span2 = self.soup.new_tag('span')
                    if 'school' in education_list[1]:
                        school_name_span2.string = education_list[1]['school']
                    school_name2.append(school_name_span2)
                    
                    # 添加时间
                    time_elem2 = self.soup.new_tag('div')
                    time_elem2['class'] = ['text-primary', 'font-medium', 'mb-4', 'flex', 'items-center', 'gap-2']
                    time_icon2 = self.soup.new_tag('i')
                    time_icon2['class'] = ['fa', 'fa-calendar', 'text-primary']
                    time_elem2.append(time_icon2)
                    if 'time' in education_list[1]:
                        time_elem2.append(education_list[1]['time'])
                    panel2.append(time_elem2)
                    
                    # 添加专业
                    major_elem2 = self.soup.new_tag('div')
                    major_elem2['class'] = ['text-medium', 'bg-primary/10', 'text-primary', 'px-4', 'py-2', 'rounded-full', 'text-sm', 'mb-6', 'inline-block']
                    if 'major' in education_list[1]:
                        major_elem2.string = education_list[1]['major']
                    panel2.append(major_elem2)
                    
                    # 添加主修课程
                    if 'courses' in education_list[1] and education_list[1]['courses']:
                        course_card2 = self.soup.new_tag('div')
                        course_card2['class'] = ['bg-gradient-to-br', 'from-purple-50', 'to-blue-50', 'rounded-xl', 'p-6', 'shadow-sm', 'mt-6']
                        panel2.append(course_card2)
                        
                        course_title2 = self.soup.new_tag('h3')
                        course_title2['class'] = ['font-medium', 'mb-6', 'flex', 'items-center', 'gap-3', 'text-lg', 'text-gray-800']
                        course_card2.append(course_title2)
                        
                        course_icon2 = self.soup.new_tag('i')
                        course_icon2['class'] = ['fa', 'fa-book', 'text-primary']
                        course_title2.append(course_icon2)
                        
                        course_title_span2 = self.soup.new_tag('span')
                        course_title_span2.string = '主修课程'
                        course_title2.append(course_title_span2)
                        
                        # 创建课程容器
                        course_container2 = self.soup.new_tag('div')
                        course_container2['class'] = ['relative']
                        course_card2.append(course_container2)
                        
                        # 创建课程网格
                        course_grid2 = self.soup.new_tag('div')
                        course_grid2['id'] = 'courses-grid-2'
                        course_grid2['class'] = ['grid', 'grid-cols-1', 'sm:grid-cols-2', 'md:grid-cols-3', 'gap-4', 'max-h-64', 'overflow-hidden', 'transition-all', 'duration-500']
                        course_container2.append(course_grid2)
                        
                        for course in education_list[1]['courses']:
                            course_div2 = self.soup.new_tag('div')
                            course_div2['class'] = ['bg-white', 'px-4', 'py-3', 'rounded-lg', 'text-sm', 'text-medium', 'shadow-sm', 'hover:shadow-md', 'transition-all', 'duration-300', 'transform', 'hover:scale-105', 'border', 'border-gray-100']
                            course_div2.string = course
                            course_grid2.append(course_div2)
                        
                        # 添加展开/收起按钮
                        if len(education_list[1]['courses']) > 8:  # 假设每行显示2-3个课程，4行大约8-12个课程
                            toggle_btn2 = self.soup.new_tag('button')
                            toggle_btn2['id'] = 'toggle-courses-2'
                            toggle_btn2['class'] = ['mt-4', 'text-primary', 'font-medium', 'flex', 'items-center', 'gap-2', 'hover:underline', 'focus:outline-none']
                            toggle_btn2.string = '展开全部'
                            toggle_icon2 = self.soup.new_tag('i')
                            toggle_icon2['class'] = ['fa', 'fa-chevron-down']
                            toggle_btn2.append(toggle_icon2)
                            course_card2.append(toggle_btn2)
                    
                    # 添加标签切换脚本
                    script = self.soup.new_tag('script')
                    script.string = '''
                        // 教育背景标签切换逻辑
                        document.addEventListener('DOMContentLoaded', function() {
                            const tabs = document.querySelectorAll('[id^="tab-education-"]');
                            const panels = document.querySelectorAll('[id^="panel-education-"]');
                            
                            tabs.forEach((tab, index) => {
                                tab.addEventListener('click', function() {
                                    // 激活当前标签
                                    tabs.forEach(t => {
                                        // 移除所有激活状态的类
                                        t.classList.remove('shadow-lg', 'transform', 'scale-105');
                                        t.classList.add('shadow-md');
                                    });
                                    // 激活当前标签
                                    tab.classList.add('shadow-lg', 'transform', 'scale-105');
                                    tab.classList.remove('shadow-md');
                                    
                                    // 显示当前面板
                                    panels.forEach(p => {
                                        p.classList.add('hidden');
                                        p.classList.remove('animate-fade-in');
                                    });
                                    panels[index].classList.remove('hidden');
                                    panels[index].classList.add('animate-fade-in');
                                });
                            });
                            
                            // 主修课程折叠逻辑
                            const toggleBtn1 = document.getElementById('toggle-courses-1');
                            const coursesGrid1 = document.getElementById('courses-grid-1');
                            
                            if (toggleBtn1 && coursesGrid1) {
                                toggleBtn1.addEventListener('click', function() {
                                    if (coursesGrid1.classList.contains('max-h-64')) {
                                        // 展开
                                        coursesGrid1.classList.remove('max-h-64');
                                        coursesGrid1.classList.add('max-h-[none]');
                                        toggleBtn1.innerHTML = '收起 <i class="fa fa-chevron-up"></i>';
                                    } else {
                                        // 收起
                                        coursesGrid1.classList.add('max-h-64');
                                        coursesGrid1.classList.remove('max-h-[none]');
                                        toggleBtn1.innerHTML = '展开全部 <i class="fa fa-chevron-down"></i>';
                                    }
                                });
                            }
                            
                            const toggleBtn2 = document.getElementById('toggle-courses-2');
                            const coursesGrid2 = document.getElementById('courses-grid-2');
                            
                            if (toggleBtn2 && coursesGrid2) {
                                toggleBtn2.addEventListener('click', function() {
                                    if (coursesGrid2.classList.contains('max-h-64')) {
                                        // 展开
                                        coursesGrid2.classList.remove('max-h-64');
                                        coursesGrid2.classList.add('max-h-[none]');
                                        toggleBtn2.innerHTML = '收起 <i class="fa fa-chevron-up"></i>';
                                    } else {
                                        // 收起
                                        coursesGrid2.classList.add('max-h-64');
                                        coursesGrid2.classList.remove('max-h-[none]');
                                        toggleBtn2.innerHTML = '展开全部 <i class="fa fa-chevron-down"></i>';
                                    }
                                });
                            }
                        });
                    '''
                    container.append(script)
                    
                    # 添加自定义样式
                    style = self.soup.new_tag('style')
                    style.string = '''
                        /* 教育背景样式 */
                        @keyframes fadeIn {
                            from {
                                opacity: 0;
                                transform: translateY(10px);
                            }
                            to {
                                opacity: 1;
                                transform: translateY(0);
                            }
                        }
                        
                        .animate-fade-in {
                            animation: fadeIn 0.5s ease-out forwards;
                        }
                    '''
                    container.append(style)
                else:
                    # 只有一段教育背景，使用单一布局
                    for i, education in enumerate(education_list):
                        # 创建院校信息卡片
                        school_card = self.soup.new_tag('div')
                        school_card['class'] = ['bg-white', 'rounded-xl', 'p-8', 'shadow-lg', 'overflow-hidden', 'border', 'border-gray-100', 'mb-8']
                        content_container.append(school_card)
                        
                        # 添加学校名称
                        school_name = self.soup.new_tag('div')
                        school_name['class'] = ['font-semibold', 'text-xl', 'flex', 'items-center', 'gap-3', 'mb-4']
                        school_card.append(school_name)
                        
                        school_icon = self.soup.new_tag('i')
                        school_icon['class'] = ['fa', 'fa-graduation-cap', 'text-primary', 'text-xl']
                        school_name.append(school_icon)
                        
                        school_name_span = self.soup.new_tag('span')
                        if 'school' in education:
                            school_name_span.string = education['school']
                        school_name.append(school_name_span)
                        
                        # 添加时间
                        time_elem = self.soup.new_tag('div')
                        time_elem['class'] = ['text-primary', 'font-medium', 'mb-4', 'flex', 'items-center', 'gap-2']
                        time_icon = self.soup.new_tag('i')
                        time_icon['class'] = ['fa', 'fa-calendar', 'text-primary']
                        time_elem.append(time_icon)
                        if 'time' in education:
                            time_elem.append(education['time'])
                        school_card.append(time_elem)
                        
                        # 添加专业
                        major_elem = self.soup.new_tag('div')
                        major_elem['class'] = ['text-medium', 'bg-primary/10', 'text-primary', 'px-4', 'py-2', 'rounded-full', 'text-sm', 'mb-6', 'inline-block']
                        if 'major' in education:
                            major_elem.string = education['major']
                        school_card.append(major_elem)
                        
                        # 添加主修课程
                        if 'courses' in education and education['courses']:
                            course_card = self.soup.new_tag('div')
                            course_card['class'] = ['bg-gradient-to-br', 'from-purple-50', 'to-blue-50', 'rounded-xl', 'p-6', 'shadow-sm', 'mt-6']
                            school_card.append(course_card)
                            
                            course_title = self.soup.new_tag('h3')
                            course_title['class'] = ['font-medium', 'mb-6', 'flex', 'items-center', 'gap-3', 'text-lg', 'text-gray-800']
                            course_card.append(course_title)
                            
                            course_icon = self.soup.new_tag('i')
                            course_icon['class'] = ['fa', 'fa-book', 'text-primary']
                            course_title.append(course_icon)
                            
                            course_title_span = self.soup.new_tag('span')
                            course_title_span.string = '主修课程'
                            course_title.append(course_title_span)
                            
                            # 创建课程容器
                            course_container = self.soup.new_tag('div')
                            course_container['class'] = ['relative']
                            course_card.append(course_container)
                            
                            # 创建课程网格
                            course_grid = self.soup.new_tag('div')
                            course_grid['id'] = 'courses-grid-single'
                            course_grid['class'] = ['grid', 'grid-cols-1', 'sm:grid-cols-2', 'md:grid-cols-3', 'gap-4', 'max-h-64', 'overflow-hidden', 'transition-all', 'duration-500']
                            course_container.append(course_grid)
                            
                            for course in education['courses']:
                                course_div = self.soup.new_tag('div')
                                course_div['class'] = ['bg-white', 'px-4', 'py-3', 'rounded-lg', 'text-sm', 'text-medium', 'shadow-sm', 'hover:shadow-md', 'transition-all', 'duration-300', 'transform', 'hover:scale-105', 'border', 'border-gray-100']
                                course_div.string = course
                                course_grid.append(course_div)
                            
                            # 添加展开/收起按钮
                            if len(education['courses']) > 8:  # 假设每行显示2-3个课程，4行大约8-12个课程
                                toggle_btn = self.soup.new_tag('button')
                                toggle_btn['id'] = 'toggle-courses-single'
                                toggle_btn['class'] = ['mt-4', 'text-primary', 'font-medium', 'flex', 'items-center', 'gap-2', 'hover:underline', 'focus:outline-none']
                                toggle_btn.string = '展开全部'
                                toggle_icon = self.soup.new_tag('i')
                                toggle_icon['class'] = ['fa', 'fa-chevron-down']
                                toggle_btn.append(toggle_icon)
                                course_card.append(toggle_btn)
                    
                    # 添加单一教育背景的折叠脚本
                    single_education_script = self.soup.new_tag('script')
                    single_education_script.string = '''
                        // 单一教育背景的主修课程折叠逻辑
                        document.addEventListener('DOMContentLoaded', function() {
                            const toggleBtn = document.getElementById('toggle-courses-single');
                            const coursesGrid = document.getElementById('courses-grid-single');
                            
                            if (toggleBtn && coursesGrid) {
                                toggleBtn.addEventListener('click', function() {
                                    if (coursesGrid.classList.contains('max-h-64')) {
                                        // 展开
                                        coursesGrid.classList.remove('max-h-64');
                                        coursesGrid.classList.add('max-h-[none]');
                                        toggleBtn.innerHTML = '收起 <i class="fa fa-chevron-up"></i>';
                                    } else {
                                        // 收起
                                        coursesGrid.classList.add('max-h-64');
                                        coursesGrid.classList.remove('max-h-[none]');
                                        toggleBtn.innerHTML = '展开全部 <i class="fa fa-chevron-down"></i>';
                                    }
                                });
                            }
                        });
                    '''
                    container.append(single_education_script)
            
            print("✓ 成功更新教育背景")
            return True
        except Exception as e:
            print(f"✗ 更新教育背景失败: {e}")
            return False
    
    def extract_experience(self):
        """提取实习经历信息"""
        experience_list = []
        
        # 提取实习经历 - 匹配实习经历后面的下一个标题，可能是工作经历或校园经历
        # 修复：使用\n+匹配一个或多个换行符，更灵活
        exp_match = re.search(r'## 实习经历\n+(.*?)(?=## \w+)', self.resume_content, re.DOTALL)
        if exp_match:
            exp_content = exp_match.group(1).strip()
            
            # 分割实习经历记录 - 按<div style="display: flex; justify-content: space-between; align-items: center;">分割
            exp_records = exp_content.split('<div style="display: flex; justify-content: space-between; align-items: center;">')
            
            # 跳过第一个空字符串（因为分割后第一个元素是空的）
            for i, record in enumerate(exp_records[1:]):
                if record.strip():
                    # 处理单个实习经历记录
                    experience = {}
                    
                    # 提取HTML部分的内容
                    html_start = record.find('<div')
                    html_end = record.rfind('</div>')
                    
                    if html_start != -1 and html_end != -1:
                        # 提取HTML部分
                        html_content = record[html_start:html_end+6]
                        # 提取剩余的Markdown部分
                        markdown_content = record[html_end+6:].strip()
                        experience['description'] = markdown_content
                        
                        # 使用更简单的方法提取公司信息、时间和职位
                        # 提取所有的粗体内容
                        bold_contents = re.findall(r'<b>(.*?)</b>', html_content, re.DOTALL)
                        if len(bold_contents) >= 3:
                            # 第一个是公司信息
                            company = bold_contents[0].strip().replace('<br>', ' ')
                            experience['company'] = company
                            # 第二个是时间
                            experience['time'] = bold_contents[1].strip()
                            # 第三个是职位
                            experience['position'] = bold_contents[2].strip()
                    else:
                        # 全部作为Markdown处理
                        experience['description'] = record
                    
                    if experience:
                        experience_list.append(experience)
        
        return experience_list
    
    def extract_work_experience(self):
        """提取工作经历信息"""
        work_experience_list = []
        
        # 提取工作经历 - 匹配工作经历后面的下一个标题
        work_match = re.search(r'## 工作经历\n\n(.*?)(?=## \w+)', self.resume_content, re.DOTALL)
        if work_match:
            work_content = work_match.group(1).strip()
            
            # 分割工作经历记录 - 按<div style="display: flex; justify-content: space-between; align-items: center;">分割
            work_records = work_content.split('<div style="display: flex; justify-content: space-between; align-items: center;">')
            
            # 跳过第一个空字符串（因为分割后第一个元素是空的）
            for i, record in enumerate(work_records[1:]):
                if record.strip():
                    # 处理单个工作经历记录
                    work_experience = {}
                    
                    # 提取HTML部分的内容
                    html_start = record.find('<div')
                    html_end = record.rfind('</div>')
                    
                    if html_start != -1 and html_end != -1:
                        # 提取HTML部分
                        html_content = record[html_start:html_end+6]
                        # 提取剩余的Markdown部分
                        markdown_content = record[html_end+6:].strip()
                        work_experience['description'] = markdown_content
                        
                        # 使用更简单的方法提取公司信息、时间和职位
                        # 提取所有的粗体内容
                        bold_contents = re.findall(r'<b>(.*?)</b>', html_content, re.DOTALL)
                        if len(bold_contents) >= 3:
                            # 第一个是公司信息
                            company = bold_contents[0].strip().replace('<br>', ' ')
                            work_experience['company'] = company
                            # 第二个是时间
                            work_experience['time'] = bold_contents[1].strip()
                            # 第三个是职位
                            work_experience['position'] = bold_contents[2].strip()
                    else:
                        # 全部作为Markdown处理
                        work_experience['description'] = record
                    
                    if work_experience:
                        work_experience_list.append(work_experience)
        
        return work_experience_list
    
    def update_experience(self):
        """更新实习经历信息"""
        experience_list = self.extract_experience()
        
        if not experience_list:
            print("✗ 未提取到实习经历信息，不加载该部分")
            # 如果没有实习经历，移除网页中的实习经历部分
            exp_section = self.soup.find('section', id='experience')
            if exp_section:
                exp_section.decompose()
            # 移除导航栏中的实习经历链接
            nav = self.soup.find('nav')
            if nav:
                exp_link = nav.find('a', href='#experience')
                if exp_link:
                    exp_link.decompose()
            # 移除移动端导航栏中的实习经历链接
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                mobile_exp_link = mobile_nav.find('a', href='#experience')
                if mobile_exp_link:
                    mobile_exp_link.decompose()
            return True
        
        try:
            # 更新实习经历卡片
            exp_section = self.soup.find('section', id='experience')
            if not exp_section:
                # 如果没有实习经历部分，创建一个
                exp_section = self.soup.new_tag('section')
                exp_section['id'] = 'experience'
                exp_section['class'] = ['py-20', 'bg-gradient-to-r', 'from-green-50', 'to-teal-50']
                
                # 找到教育背景部分，在其后插入实习经历部分
                edu_section = self.soup.find('section', id='education')
                if edu_section:
                    edu_section.insert_after(exp_section)
                else:
                    # 如果没有教育背景部分，在个人信息部分后插入
                    info_section = self.soup.find('section', id='info')
                    if info_section:
                        info_section.insert_after(exp_section)
            
            # 清空现有内容
            exp_section.clear()
            
            # 创建容器
            container = self.soup.new_tag('div')
            container['class'] = ['container', 'mx-auto', 'px-4']
            exp_section.append(container)
            
            # 创建标题
            title_div = self.soup.new_tag('div')
            title_div['class'] = ['text-center', 'mb-12']
            title_h2 = self.soup.new_tag('h2')
            title_h2['class'] = ['text-3xl', 'font-bold', 'mb-2']
            title_h2.string = '实习经历'
            title_div.append(title_h2)
            title_line = self.soup.new_tag('div')
            title_line['class'] = ['w-20', 'h-1', 'bg-primary', 'mx-auto']
            title_div.append(title_line)
            container.append(title_div)
            
            # 创建新的内容容器
            content_container = self.soup.new_tag('div')
            content_container['class'] = ['max-w-4xl', 'mx-auto']
            container.append(content_container)
            
            # 如果有多个实习经历，使用标签栏切换布局
            if len(experience_list) > 1:
                # 创建标签栏容器
                tab_container = self.soup.new_tag('div')
                tab_container['class'] = ['mb-8']
                content_container.append(tab_container)
                
                # 创建标签按钮组
                tab_buttons = self.soup.new_tag('div')
                tab_buttons['class'] = ['flex', 'justify-center', 'gap-4', 'p-2']
                tab_container.append(tab_buttons)
                
                # 创建标签按钮和内容面板
                panels = []
                colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-pink-500', 'bg-yellow-500', 'bg-orange-500', 'bg-teal-500']  # 多彩颜色
                for i, exp in enumerate(experience_list):
                    # 创建标签按钮
                    tab_button = self.soup.new_tag('button')
                    tab_button['id'] = f'tab-experience-{i+1}'
                    color_class = colors[i % len(colors)]
                    if i == 0:
                        tab_button['class'] = [f'w-16', 'h-16', 'rounded-full', color_class, 'text-white', 'flex', 'items-center', 'justify-center', 'shadow-lg', 'transition-all', 'duration-300', 'transform', 'scale-105', 'focus:outline-none', 'focus:ring-2', f'focus:ring-{color_class.replace("bg-", "")}/20']
                    else:
                        tab_button['class'] = [f'w-16', 'h-16', 'rounded-full', color_class, 'text-white', 'flex', 'items-center', 'justify-center', 'shadow-md', f'hover:{color_class}/80', 'transition-all', 'duration-300', 'focus:outline-none', 'focus:ring-2', f'focus:ring-{color_class.replace("bg-", "")}/20']
                    # 添加图标
                    tab_icon = self.soup.new_tag('i')
                    tab_icon['class'] = ['fa', 'fa-briefcase', 'text-xl']
                    tab_button.append(tab_icon)
                    tab_buttons.append(tab_button)
                
                # 创建内容容器
                content_wrapper = self.soup.new_tag('div')
                content_wrapper['class'] = ['bg-white', 'rounded-xl', 'shadow-lg', 'overflow-hidden', 'border', 'border-gray-100']
                content_container.append(content_wrapper)
                
                # 创建内容面板
                for i, exp in enumerate(experience_list):
                    # 创建内容面板
                    panel = self.soup.new_tag('div')
                    panel['id'] = f'panel-experience-{i+1}'
                    if i == 0:
                        panel['class'] = ['p-8', 'animate-fade-in']
                    else:
                        panel['class'] = ['p-8', 'hidden', 'animate-fade-in']
                    content_wrapper.append(panel)
                    panels.append(panel)
                    
                    # 按照网页样式添加公司信息、时间和职位
                    if 'company' in exp and 'time' in exp and 'position' in exp:
                        # 创建公司信息、时间和职位的容器
                        info_container = self.soup.new_tag('div')
                        info_container['class'] = ['flex', 'flex-col', 'md:flex-row', 'justify-between', 'items-start', 'md:items-center', 'mb-6']
                        panel.append(info_container)
                        
                        # 添加公司信息
                        company_div = self.soup.new_tag('div')
                        company_div['class'] = ['font-semibold', 'text-xl', 'mb-4', 'md:mb-0']
                        company_div.string = exp['company']
                        info_container.append(company_div)
                        
                        # 添加时间
                        time_div = self.soup.new_tag('div')
                        time_div['class'] = ['text-primary', 'font-medium', 'mb-4', 'md:mb-0', 'flex', 'items-center', 'gap-2']
                        time_icon = self.soup.new_tag('i')
                        time_icon['class'] = ['fa', 'fa-calendar', 'text-primary']
                        time_div.append(time_icon)
                        time_div.append(exp['time'])
                        info_container.append(time_div)
                        
                        # 添加职位
                        position_div = self.soup.new_tag('div')
                        position_div['class'] = ['text-medium', 'bg-primary/10', 'text-primary', 'px-4', 'py-2', 'rounded-full', 'text-sm']
                        position_div.string = exp['position']
                        info_container.append(position_div)
                    
                    # 添加描述内容
                    if 'description' in exp and exp['description']:
                        # 转换Markdown为HTML
                        markdown_html = markdown.markdown(exp['description'])
                        desc_container = BeautifulSoup(markdown_html, 'html.parser')
                        panel.append(desc_container)
                
                # 添加标签切换脚本
                script = self.soup.new_tag('script')
                script.string = '''
                    // 实习经历标签切换逻辑
                    document.addEventListener('DOMContentLoaded', function() {
                        const tabs = document.querySelectorAll('[id^="tab-experience-"]');
                        const panels = document.querySelectorAll('[id^="panel-experience-"]');
                        
                        tabs.forEach((tab, index) => {
                            tab.addEventListener('click', function() {
                                // 激活当前标签
                                tabs.forEach(t => {
                                    // 移除所有激活状态的类
                                    t.classList.remove('shadow-lg', 'transform', 'scale-105');
                                    t.classList.add('shadow-md');
                                });
                                // 激活当前标签
                                tab.classList.add('shadow-lg', 'transform', 'scale-105');
                                tab.classList.remove('shadow-md');
                                
                                // 显示当前面板
                                panels.forEach(p => {
                                    p.classList.add('hidden');
                                    p.classList.remove('animate-fade-in');
                                });
                                panels[index].classList.remove('hidden');
                                panels[index].classList.add('animate-fade-in');
                            });
                        });
                    });
                '''
                container.append(script)
            else:
                # 只有一段实习经历，使用单一布局
                for i, exp in enumerate(experience_list):
                    # 创建实习经历卡片
                    card = self.soup.new_tag('div')
                    card['class'] = ['bg-white', 'rounded-xl', 'p-8', 'shadow-lg', 'overflow-hidden', 'border', 'border-gray-100', 'mb-8']
                    content_container.append(card)
                    
                    # 按照网页样式添加公司信息、时间和职位
                    if 'company' in exp and 'time' in exp and 'position' in exp:
                        # 创建公司信息、时间和职位的容器
                        info_container = self.soup.new_tag('div')
                        info_container['class'] = ['flex', 'flex-col', 'md:flex-row', 'justify-between', 'items-start', 'md:items-center', 'mb-6']
                        card.append(info_container)
                        
                        # 添加公司信息
                        company_div = self.soup.new_tag('div')
                        company_div['class'] = ['font-semibold', 'text-xl', 'mb-4', 'md:mb-0']
                        company_div.string = exp['company']
                        info_container.append(company_div)
                        
                        # 添加时间
                        time_div = self.soup.new_tag('div')
                        time_div['class'] = ['text-primary', 'font-medium', 'mb-4', 'md:mb-0', 'flex', 'items-center', 'gap-2']
                        time_icon = self.soup.new_tag('i')
                        time_icon['class'] = ['fa', 'fa-calendar', 'text-primary']
                        time_div.append(time_icon)
                        time_div.append(exp['time'])
                        info_container.append(time_div)
                        
                        # 添加职位
                        position_div = self.soup.new_tag('div')
                        position_div['class'] = ['text-medium', 'bg-primary/10', 'text-primary', 'px-4', 'py-2', 'rounded-full', 'text-sm']
                        position_div.string = exp['position']
                        info_container.append(position_div)
                    
                    # 添加描述内容
                    if 'description' in exp and exp['description']:
                        # 转换Markdown为HTML
                        markdown_html = markdown.markdown(exp['description'])
                        desc_container = BeautifulSoup(markdown_html, 'html.parser')
                        card.append(desc_container)
            
            # 更新导航栏，添加实习经历链接
            nav = self.soup.find('nav')
            if nav:
                # 检查是否已经存在实习经历链接
                existing_exp_link = nav.find('a', href='#experience')
                if not existing_exp_link:
                    # 找到教育背景链接
                    edu_link = nav.find('a', href='#education')
                    if edu_link:
                        # 在教育背景链接后添加实习经历链接
                        exp_link = self.soup.new_tag('a')
                        exp_link['href'] = '#experience'
                        exp_link['class'] = ['text-medium', 'hover:text-primary', 'transition-colors', 'duration-300']
                        exp_link.string = '实习经历'
                        edu_link.insert_after(exp_link)
            
            # 更新移动端导航栏
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                # 检查是否已经存在实习经历链接
                existing_mobile_exp_link = mobile_nav.find('a', href='#experience')
                if not existing_mobile_exp_link:
                    # 找到教育背景链接
                    mobile_edu_link = mobile_nav.find('a', href='#education')
                    if mobile_edu_link:
                        # 在教育背景链接后添加实习经历链接
                        mobile_exp_link = self.soup.new_tag('a')
                        mobile_exp_link['href'] = '#experience'
                        mobile_exp_link['class'] = ['text-medium', 'hover:text-primary', 'transition-colors', 'duration-300']
                        mobile_exp_link.string = '实习经历'
                        mobile_edu_link.insert_after(mobile_exp_link)
            
            print("✓ 成功更新实习经历")
            return True
        except Exception as e:
            print(f"✗ 更新实习经历失败: {e}")
            return False
    
    def update_work_experience(self):
        """更新工作经历信息"""
        work_experience_list = self.extract_work_experience()
        
        if not work_experience_list:
            print("✗ 未提取到工作经历信息，不加载该部分")
            # 如果没有工作经历，移除网页中的工作经历部分
            work_section = self.soup.find('section', id='work')
            if work_section:
                work_section.decompose()
            # 移除导航栏中的工作经历链接
            nav = self.soup.find('nav')
            if nav:
                work_link = nav.find('a', href='#work')
                if work_link:
                    work_link.decompose()
            # 移除移动端导航栏中的工作经历链接
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                mobile_work_link = mobile_nav.find('a', href='#work')
                if mobile_work_link:
                    mobile_work_link.decompose()
            # 移除工作经历的注释标记
            for comment in self.soup.find_all(text=lambda text: isinstance(text, str) and '<!-- 工作经历 -->' in text):
                comment.extract()
            return True
        
        try:
            # 更新工作经历卡片
            work_section = self.soup.find('section', id='work')
            if not work_section:
                # 如果没有工作经历部分，创建一个
                work_section = self.soup.new_tag('section')
                work_section['id'] = 'work'
                work_section['class'] = ['py-20', 'bg-gradient-to-r', 'from-blue-50', 'to-indigo-50']
                
                # 找到实习经历部分，在其后插入工作经历部分
                exp_section = self.soup.find('section', id='experience')
                if exp_section:
                    exp_section.insert_after(work_section)
                else:
                    # 如果没有实习经历部分，在校园经历部分前插入
                    campus_section = self.soup.find('section', id='campus')
                    if campus_section:
                        campus_section.insert_before(work_section)
            
            # 清空工作经历部分的现有内容
            work_section.clear()
            
            # 创建容器
            container = self.soup.new_tag('div')
            container['class'] = ['container', 'mx-auto', 'px-4']
            work_section.append(container)
            
            # 创建标题
            title_div = self.soup.new_tag('div')
            title_div['class'] = ['text-center', 'mb-12']
            title_h2 = self.soup.new_tag('h2')
            title_h2['class'] = ['text-3xl', 'font-bold', 'mb-2']
            title_h2.string = '工作经历'
            title_div.append(title_h2)
            title_line = self.soup.new_tag('div')
            title_line['class'] = ['w-20', 'h-1', 'bg-primary', 'mx-auto']
            title_div.append(title_line)
            container.append(title_div)
            
            # 创建新的内容容器
            content_container = self.soup.new_tag('div')
            content_container['class'] = ['max-w-4xl', 'mx-auto']
            container.append(content_container)
            
            # 如果有多个工作经历，使用标签栏切换布局
            if len(work_experience_list) > 1:
                # 创建标签栏容器
                tab_container = self.soup.new_tag('div')
                tab_container['class'] = ['mb-8']
                content_container.append(tab_container)
                
                # 创建标签按钮组
                tab_buttons = self.soup.new_tag('div')
                tab_buttons['class'] = ['flex', 'justify-center', 'gap-4', 'p-2']
                tab_container.append(tab_buttons)
                
                # 创建标签按钮和内容面板
                panels = []
                colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-pink-500', 'bg-yellow-500', 'bg-orange-500', 'bg-teal-500']  # 多彩颜色
                for i, exp in enumerate(work_experience_list):
                    # 创建标签按钮
                    tab_button = self.soup.new_tag('button')
                    tab_button['id'] = f'tab-work-{i+1}'
                    color_class = colors[i % len(colors)]
                    if i == 0:
                        tab_button['class'] = [f'w-16', 'h-16', 'rounded-full', color_class, 'text-white', 'flex', 'items-center', 'justify-center', 'shadow-lg', 'transition-all', 'duration-300', 'transform', 'scale-105', 'focus:outline-none', 'focus:ring-2', f'focus:ring-{color_class.replace("bg-", "")}/20']
                    else:
                        tab_button['class'] = [f'w-16', 'h-16', 'rounded-full', color_class, 'text-white', 'flex', 'items-center', 'justify-center', 'shadow-md', f'hover:{color_class}/80', 'transition-all', 'duration-300', 'focus:outline-none', 'focus:ring-2', f'focus:ring-{color_class.replace("bg-", "")}/20']
                    # 添加图标
                    tab_icon = self.soup.new_tag('i')
                    tab_icon['class'] = ['fa', 'fa-briefcase', 'text-xl']
                    tab_button.append(tab_icon)
                    tab_buttons.append(tab_button)
                
                # 创建内容容器
                content_wrapper = self.soup.new_tag('div')
                content_wrapper['class'] = ['bg-white', 'rounded-xl', 'shadow-lg', 'overflow-hidden', 'border', 'border-gray-100']
                content_container.append(content_wrapper)
                
                # 创建内容面板
                for i, exp in enumerate(work_experience_list):
                    # 创建内容面板
                    panel = self.soup.new_tag('div')
                    panel['id'] = f'panel-work-{i+1}'
                    if i == 0:
                        panel['class'] = ['p-8', 'animate-fade-in']
                    else:
                        panel['class'] = ['p-8', 'hidden', 'animate-fade-in']
                    content_wrapper.append(panel)
                    panels.append(panel)
                    
                    # 按照网页样式添加公司信息、时间和职位
                    if 'company' in exp and 'time' in exp and 'position' in exp:
                        # 创建公司信息、时间和职位的容器
                        info_container = self.soup.new_tag('div')
                        info_container['class'] = ['flex', 'flex-col', 'md:flex-row', 'justify-between', 'items-start', 'md:items-center', 'mb-6']
                        panel.append(info_container)
                        
                        # 添加公司信息
                        company_div = self.soup.new_tag('div')
                        company_div['class'] = ['font-semibold', 'text-xl', 'mb-4', 'md:mb-0']
                        company_div.string = exp['company']
                        info_container.append(company_div)
                        
                        # 添加时间
                        time_div = self.soup.new_tag('div')
                        time_div['class'] = ['text-primary', 'font-medium', 'mb-4', 'md:mb-0', 'flex', 'items-center', 'gap-2']
                        time_icon = self.soup.new_tag('i')
                        time_icon['class'] = ['fa', 'fa-calendar', 'text-primary']
                        time_div.append(time_icon)
                        time_div.append(exp['time'])
                        info_container.append(time_div)
                        
                        # 添加职位
                        position_div = self.soup.new_tag('div')
                        position_div['class'] = ['text-medium', 'bg-primary/10', 'text-primary', 'px-4', 'py-2', 'rounded-full', 'text-sm']
                        position_div.string = exp['position']
                        info_container.append(position_div)
                    
                    # 添加描述内容
                    if 'description' in exp and exp['description']:
                        # 转换Markdown为HTML
                        markdown_html = markdown.markdown(exp['description'])
                        desc_container = BeautifulSoup(markdown_html, 'html.parser')
                        panel.append(desc_container)
                
                # 添加标签切换脚本
                script = self.soup.new_tag('script')
                script.string = '''
                    // 工作经历标签切换逻辑
                    document.addEventListener('DOMContentLoaded', function() {
                        const tabs = document.querySelectorAll('[id^="tab-work-"]');
                        const panels = document.querySelectorAll('[id^="panel-work-"]');
                        
                        tabs.forEach((tab, index) => {
                            tab.addEventListener('click', function() {
                                // 激活当前标签
                                tabs.forEach(t => {
                                    // 移除所有激活状态的类
                                    t.classList.remove('shadow-lg', 'transform', 'scale-105');
                                    t.classList.add('shadow-md');
                                });
                                // 激活当前标签
                                tab.classList.add('shadow-lg', 'transform', 'scale-105');
                                tab.classList.remove('shadow-md');
                                
                                // 显示当前面板
                                panels.forEach(p => {
                                    p.classList.add('hidden');
                                    p.classList.remove('animate-fade-in');
                                });
                                panels[index].classList.remove('hidden');
                                panels[index].classList.add('animate-fade-in');
                            });
                        });
                    });
                '''
                container.append(script)
            else:
                # 只有一段工作经历，使用单一布局
                for i, exp in enumerate(work_experience_list):
                    # 创建工作经历卡片
                    card = self.soup.new_tag('div')
                    card['class'] = ['bg-white', 'rounded-xl', 'p-8', 'shadow-lg', 'overflow-hidden', 'border', 'border-gray-100', 'mb-8']
                    content_container.append(card)
                    
                    # 按照网页样式添加公司信息、时间和职位
                    if 'company' in exp and 'time' in exp and 'position' in exp:
                        # 创建公司信息、时间和职位的容器
                        info_container = self.soup.new_tag('div')
                        info_container['class'] = ['flex', 'flex-col', 'md:flex-row', 'justify-between', 'items-start', 'md:items-center', 'mb-6']
                        card.append(info_container)
                        
                        # 添加公司信息
                        company_div = self.soup.new_tag('div')
                        company_div['class'] = ['font-semibold', 'text-xl', 'mb-4', 'md:mb-0']
                        company_div.string = exp['company']
                        info_container.append(company_div)
                        
                        # 添加时间
                        time_div = self.soup.new_tag('div')
                        time_div['class'] = ['text-primary', 'font-medium', 'mb-4', 'md:mb-0', 'flex', 'items-center', 'gap-2']
                        time_icon = self.soup.new_tag('i')
                        time_icon['class'] = ['fa', 'fa-calendar', 'text-primary']
                        time_div.append(time_icon)
                        time_div.append(exp['time'])
                        info_container.append(time_div)
                        
                        # 添加职位
                        position_div = self.soup.new_tag('div')
                        position_div['class'] = ['text-medium', 'bg-primary/10', 'text-primary', 'px-4', 'py-2', 'rounded-full', 'text-sm']
                        position_div.string = exp['position']
                        info_container.append(position_div)
                    
                    # 添加描述内容
                    if 'description' in exp and exp['description']:
                        # 转换Markdown为HTML
                        markdown_html = markdown.markdown(exp['description'])
                        desc_container = BeautifulSoup(markdown_html, 'html.parser')
                        card.append(desc_container)
            
            # 更新导航栏，添加工作经历链接
            nav = self.soup.find('nav')
            if nav:
                # 检查是否已经存在工作经历链接
                existing_work_link = nav.find('a', href='#work')
                if not existing_work_link:
                    # 找到实习经历链接
                    exp_link = nav.find('a', href='#experience')
                    if exp_link:
                        # 在实习经历链接后添加工作经历链接
                        work_link = self.soup.new_tag('a')
                        work_link['href'] = '#work'
                        work_link['class'] = ['text-medium', 'hover:text-primary', 'transition-colors', 'duration-300']
                        work_link.string = '工作经历'
                        exp_link.insert_after(work_link)
            
            # 更新移动端导航栏
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                # 检查是否已经存在工作经历链接
                existing_mobile_work_link = mobile_nav.find('a', href='#work')
                if not existing_mobile_work_link:
                    # 找到实习经历链接
                    mobile_exp_link = mobile_nav.find('a', href='#experience')
                    if mobile_exp_link:
                        # 在实习经历链接后添加工作经历链接
                        mobile_work_link = self.soup.new_tag('a')
                        mobile_work_link['href'] = '#work'
                        mobile_work_link['class'] = ['text-medium', 'hover:text-primary', 'transition-colors', 'duration-300']
                        mobile_work_link.string = '工作经历'
                        mobile_exp_link.insert_after(mobile_work_link)
            
            print("✓ 成功更新工作经历")
            return True
        except Exception as e:
            print(f"✗ 更新工作经历失败: {e}")
            return False
    
    def extract_campus_experience(self):
        """提取校园经历信息"""
        campus_experiences = []
        
        # 提取校园经历
        # 修复：使用\n+匹配一个或多个换行符，更灵活
        campus_match = re.search(r'## 校园经历\n+(.*?)## 个人项目', self.resume_content, re.DOTALL)
        if campus_match:
            campus_content = campus_match.group(1).strip()
            
            # 提取每条经历 - 使用更可靠的方法
            # 按行分割
            lines = campus_content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    # 移除开头的 '- '
                    exp = line[2:].strip()
                    if exp:
                        # 提取时间和内容 - 处理不同类型的分隔符
                        # 尝试不同的分隔符
                        time_match = re.search(r'(\d{4}\.\d{2})\s*[|｜]\s*(.*)', exp)
                        if time_match:
                            time = time_match.group(1).strip()
                            content = time_match.group(2).strip()
                        else:
                            # 尝试没有分隔符的情况
                            time_match = re.search(r'(\d{4}\.\d{2})\s*(.*)', exp)
                            if time_match:
                                time = time_match.group(1).strip()
                                content = time_match.group(2).strip()
                        
                        if time_match:
                            # 提取描述
                            desc_match = re.search(r'—— (.*)', content)
                            if desc_match:
                                activity = content.split('——')[0].strip()
                                description = desc_match.group(1).strip()
                            else:
                                activity = content.strip()
                                description = ""
                            
                            campus_experiences.append({
                                'time': time,
                                'activity': activity,
                                'description': description
                            })
        
        return campus_experiences
    
    def update_campus_experience(self):
        """更新校园经历信息"""
        campus_experiences = self.extract_campus_experience()
        
        if not campus_experiences:
            print("✗ 未提取到校园经历信息，不加载该部分")
            # 如果没有校园经历，移除网页中的校园经历部分
            campus_section = self.soup.find('section', id='campus')
            if campus_section:
                campus_section.decompose()
            # 移除导航栏中的校园经历链接
            nav = self.soup.find('nav')
            if nav:
                campus_link = nav.find('a', href='#campus')
                if campus_link:
                    campus_link.decompose()
            # 移除移动端导航栏中的校园经历链接
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                mobile_campus_link = mobile_nav.find('a', href='#campus')
                if mobile_campus_link:
                    mobile_campus_link.decompose()
            # 移除校园经历的注释标记
            for comment in self.soup.find_all(text=lambda text: isinstance(text, str) and '<!-- 校园经历 -->' in text):
                comment.extract()
            return True
        
        try:
            # 更新校园经历列表
            campus_section = self.soup.find('section', id='campus')
            if not campus_section:
                # 如果没有校园经历部分，创建一个
                campus_section = self.soup.new_tag('section')
                campus_section['id'] = 'campus'
                campus_section['class'] = ['py-20', 'bg-gradient-to-r', 'from-yellow-50', 'to-orange-50']
                
                # 找到实习经历部分，在其后插入校园经历部分
                exp_section = self.soup.find('section', id='experience')
                if exp_section:
                    exp_section.insert_after(campus_section)
                else:
                    # 找到教育背景部分，在其后插入校园经历部分
                    edu_section = self.soup.find('section', id='education')
                    if edu_section:
                        edu_section.insert_after(campus_section)
                    else:
                        # 如果没有教育背景部分，在个人信息部分后插入
                        info_section = self.soup.find('section', id='info')
                        if info_section:
                            info_section.insert_after(campus_section)
            
            # 清空现有内容
            campus_section.clear()
            
            # 创建容器
            container = self.soup.new_tag('div')
            container['class'] = ['container', 'mx-auto', 'px-4']
            campus_section.append(container)
            
            # 创建标题
            title_div = self.soup.new_tag('div')
            title_div['class'] = ['text-center', 'mb-12']
            title_h2 = self.soup.new_tag('h2')
            title_h2['class'] = ['text-3xl', 'font-bold', 'mb-2']
            title_h2.string = '校园经历'
            title_div.append(title_h2)
            title_line = self.soup.new_tag('div')
            title_line['class'] = ['w-20', 'h-1', 'bg-primary', 'mx-auto']
            title_div.append(title_line)
            container.append(title_div)
            
            # 创建内容容器
            content_container = self.soup.new_tag('div')
            content_container['class'] = ['max-w-4xl', 'mx-auto']
            container.append(content_container)
            
            # 创建校园经历列表容器
            campus_container = self.soup.new_tag('div')
            campus_container['class'] = ['space-y-4']
            content_container.append(campus_container)
            
            # 添加新经历
            for exp in campus_experiences:
                exp_div = self.soup.new_tag('div')
                exp_div['class'] = ['bg-white', 'rounded-lg', 'p-4', 'shadow-sm', 'hover:shadow-md', 'transition-shadow', 'duration-300']
                
                # 添加时间和活动
                time_activity_div = self.soup.new_tag('div')
                time_activity_div['class'] = ['flex', 'justify-between', 'items-center', 'mb-2']
                
                activity_span = self.soup.new_tag('div')
                activity_span['class'] = ['font-medium']
                activity_span.string = exp['activity']
                
                time_span = self.soup.new_tag('div')
                time_span['class'] = ['text-primary']
                time_span.string = exp['time']
                
                time_activity_div.append(activity_span)
                time_activity_div.append(time_span)
                
                # 添加描述
                if exp['description']:
                    desc_p = self.soup.new_tag('p')
                    desc_p['class'] = ['text-medium', 'text-sm']
                    desc_p.string = exp['description']
                    exp_div.append(time_activity_div)
                    exp_div.append(desc_p)
                else:
                    exp_div.append(time_activity_div)
                
                campus_container.append(exp_div)
            
            # 更新导航栏，添加校园经历链接
            nav = self.soup.find('nav')
            if nav:
                # 检查是否已经存在校园经历链接
                existing_campus_link = nav.find('a', href='#campus')
                if not existing_campus_link:
                    # 找到实习经历链接
                    exp_link = nav.find('a', href='#experience')
                    if exp_link:
                        # 在实习经历链接后添加校园经历链接
                        campus_link = self.soup.new_tag('a')
                        campus_link['href'] = '#campus'
                        campus_link['class'] = ['text-medium', 'hover:text-primary', 'transition-colors', 'duration-300']
                        campus_link.string = '校园经历'
                        exp_link.insert_after(campus_link)
                    else:
                        # 如果没有实习经历链接，找到教育背景链接
                        edu_link = nav.find('a', href='#education')
                        if edu_link:
                            # 在教育背景链接后添加校园经历链接
                            campus_link = self.soup.new_tag('a')
                            campus_link['href'] = '#campus'
                            campus_link['class'] = ['text-medium', 'hover:text-primary', 'transition-colors', 'duration-300']
                            campus_link.string = '校园经历'
                            edu_link.insert_after(campus_link)
            
            # 更新移动端导航栏
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                # 检查是否已经存在校园经历链接
                existing_mobile_campus_link = mobile_nav.find('a', href='#campus')
                if not existing_mobile_campus_link:
                    # 找到实习经历链接
                    mobile_exp_link = mobile_nav.find('a', href='#experience')
                    if mobile_exp_link:
                        # 在实习经历链接后添加校园经历链接
                        mobile_campus_link = self.soup.new_tag('a')
                        mobile_campus_link['href'] = '#campus'
                        mobile_campus_link['class'] = ['text-medium', 'hover:text-primary', 'transition-colors', 'duration-300']
                        mobile_campus_link.string = '校园经历'
                        mobile_exp_link.insert_after(mobile_campus_link)
                    else:
                        # 如果没有实习经历链接，找到教育背景链接
                        mobile_edu_link = mobile_nav.find('a', href='#education')
                        if mobile_edu_link:
                            # 在教育背景链接后添加校园经历链接
                            mobile_campus_link = self.soup.new_tag('a')
                            mobile_campus_link['href'] = '#campus'
                            mobile_campus_link['class'] = ['text-medium', 'hover:text-primary', 'transition-colors', 'duration-300']
                            mobile_campus_link.string = '校园经历'
                            mobile_edu_link.insert_after(mobile_campus_link)
            
            print("✓ 成功更新校园经历")
            return True
        except Exception as e:
            print(f"✗ 更新校园经历失败: {e}")
            return False
    
    def extract_projects(self):
        """提取个人项目信息"""
        projects = []
        
        # 直接从文件中读取并解析
        with open(self.resume_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 找到个人项目部分
        project_start = -1
        project_end = -1
        for i, line in enumerate(lines):
            if '## 个人项目' in line:
                project_start = i
            elif project_start != -1 and '## 专业技能' in line:
                project_end = i
                break
        
        if project_start != -1 and project_end != -1:
            # 提取项目内容
            project_lines = lines[project_start+1:project_end]
            project_content = ''.join(project_lines).strip()
            
            # 分割项目记录 - 按<div style="display: flex; justify-content: space-between; align-items: center;">分割
            project_records = project_content.split('<div style="display: flex; justify-content: space-between; align-items: center;">')
            
            # 跳过第一个空字符串（因为分割后第一个元素是空的）
            for i, record in enumerate(project_records[1:]):
                if record.strip():
                    # 处理单个项目记录
                    project = {}
                    
                    # 提取HTML部分的内容
                    html_start = record.find('<div')
                    html_end = record.rfind('</div>')
                    
                    if html_start != -1 and html_end != -1:
                        # 提取HTML部分
                        html_content = record[html_start:html_end+6]
                        # 提取剩余的Markdown部分
                        markdown_content = record[html_end+6:].strip()
                        project['description'] = markdown_content
                        
                        # 使用更简单的方法提取项目信息
                        # 提取所有的粗体内容
                        bold_contents = re.findall(r'<b>(.*?)</b>', html_content, re.DOTALL)
                        if len(bold_contents) >= 1:
                            # 第一个是项目名称
                            project['name'] = bold_contents[0].strip().replace('<br>', ' ')
                        if len(bold_contents) >= 3:
                            # 第三个是项目时间
                            project['time'] = bold_contents[2].strip()
                        elif len(bold_contents) >= 1:
                            # 如果只有一个粗体内容，尝试从其他位置提取时间
                            time_match = re.search(r'(\d{4}\.\d{1,2}——\d{4}\.\d{1,2}|\d{4}\.\d{1,2}——至今)', markdown_content)
                            if time_match:
                                project['time'] = time_match.group(1).strip()
                    else:
                        # 全部作为Markdown处理
                        project['description'] = record
                    
                    if project:
                        projects.append(project)
        
        return projects
    
    def update_projects(self):
        """更新个人项目信息"""
        projects = self.extract_projects()
        
        if not projects:
            print("✗ 未提取到个人项目信息，不加载该部分")
            # 如果没有个人项目，移除网页中的个人项目部分
            project_section = self.soup.find('section', id='projects')
            if project_section:
                project_section.decompose()
            # 移除导航栏中的个人项目链接
            nav = self.soup.find('nav')
            if nav:
                project_link = nav.find('a', href='#projects')
                if project_link:
                    project_link.decompose()
            # 移除移动端导航栏中的个人项目链接
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                mobile_project_link = mobile_nav.find('a', href='#projects')
                if mobile_project_link:
                    mobile_project_link.decompose()
            # 移除个人项目的注释标记
            for comment in self.soup.find_all(text=lambda text: isinstance(text, str) and '<!-- 个人项目 -->' in text):
                comment.extract()
            return True
        
        try:
            # 更新个人项目卡片
            project_section = self.soup.find('section', id='projects')
            if project_section:
                # 清空现有内容
                for child in project_section.find_all(recursive=False):
                    if child.name != 'div' or 'container' not in child.get('class', []):
                        child.decompose()
                
                # 找到容器
                container = project_section.find('div', class_='container')
                if not container:
                    # 如果没有容器，创建一个
                    container = self.soup.new_tag('div')
                    container['class'] = ['container', 'mx-auto', 'px-4']
                    project_section.append(container)
                
                # 清空容器内的内容，只保留标题
                title_div = container.find('div', class_='text-center')
                if not title_div:
                    # 如果没有标题，创建一个
                    title_div = self.soup.new_tag('div')
                    title_div['class'] = ['text-center', 'mb-12']
                    title_h2 = self.soup.new_tag('h2')
                    title_h2['class'] = ['text-3xl', 'font-bold', 'mb-2']
                    title_h2.string = '个人项目'
                    title_div.append(title_h2)
                    title_line = self.soup.new_tag('div')
                    title_line['class'] = ['w-20', 'h-1', 'bg-primary', 'mx-auto']
                    title_div.append(title_line)
                    container.append(title_div)
                else:
                    # 保留标题，移除其他内容
                    for child in container.find_all(recursive=False):
                        if child != title_div:
                            child.decompose()
                
                # 创建新的内容容器
                content_container = self.soup.new_tag('div')
                content_container['class'] = ['max-w-4xl', 'mx-auto']
                container.append(content_container)
                
                # 如果有多个个人项目，使用标签栏切换布局
                if len(projects) > 1:
                    # 创建标签栏容器
                    tab_container = self.soup.new_tag('div')
                    tab_container['class'] = ['mb-8']
                    content_container.append(tab_container)
                    
                    # 创建标签按钮组
                    tab_buttons = self.soup.new_tag('div')
                    tab_buttons['class'] = ['flex', 'justify-center', 'gap-4', 'p-2']
                    tab_container.append(tab_buttons)
                    
                    # 定义多彩颜色
                    colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-pink-500', 'bg-yellow-500', 'bg-orange-500', 'bg-teal-500']
                    
                    # 创建标签按钮和内容面板
                    panels = []
                    for i, project in enumerate(projects):
                        # 创建标签按钮
                        tab_button = self.soup.new_tag('button')
                        tab_button['id'] = f'tab-project-{i+1}'
                        color_class = colors[i % len(colors)]
                        if i == 0:
                            tab_button['class'] = [f'w-16', 'h-16', 'rounded-full', color_class, 'text-white', 'flex', 'items-center', 'justify-center', 'shadow-lg', 'transition-all', 'duration-300', 'transform', 'scale-105', 'focus:outline-none', 'focus:ring-2', f'focus:ring-{color_class.replace("bg-", "")}/20']
                        else:
                            tab_button['class'] = [f'w-16', 'h-16', 'rounded-full', color_class, 'text-white', 'flex', 'items-center', 'justify-center', 'shadow-md', f'hover:{color_class}/80', 'transition-all', 'duration-300', 'focus:outline-none', 'focus:ring-2', f'focus:ring-{color_class.replace("bg-", "")}/20']
                        # 添加图标
                        tab_icon = self.soup.new_tag('i')
                        tab_icon['class'] = ['fa', 'fa-code', 'text-xl']
                        tab_button.append(tab_icon)
                        tab_buttons.append(tab_button)
                    
                    # 创建内容容器
                    content_wrapper = self.soup.new_tag('div')
                    content_wrapper['class'] = ['bg-white', 'rounded-xl', 'shadow-lg', 'overflow-hidden', 'border', 'border-gray-100']
                    content_container.append(content_wrapper)
                    
                    # 创建内容面板
                    for i, project in enumerate(projects):
                        # 创建内容面板
                        panel = self.soup.new_tag('div')
                        panel['id'] = f'panel-project-{i+1}'
                        if i == 0:
                            panel['class'] = ['p-8', 'animate-fade-in']
                        else:
                            panel['class'] = ['p-8', 'hidden', 'animate-fade-in']
                        content_wrapper.append(panel)
                        panels.append(panel)
                        
                        # 添加项目信息
                        if 'name' in project and 'time' in project:
                            # 创建项目信息容器
                            info_container = self.soup.new_tag('div')
                            info_container['class'] = ['flex', 'flex-col', 'md:flex-row', 'justify-between', 'items-start', 'md:items-center', 'mb-4']
                            panel.append(info_container)
                            
                            # 添加项目名称
                            name_div = self.soup.new_tag('div')
                            name_div['class'] = ['font-semibold', 'text-lg', 'mb-2', 'md:mb-0']
                            name_div.string = project['name']
                            info_container.append(name_div)
                            
                            # 添加项目时间
                            time_div = self.soup.new_tag('div')
                            time_div['class'] = ['text-primary', 'font-medium', 'mb-2', 'md:mb-0']
                            time_div.string = project['time']
                            info_container.append(time_div)
                        
                        # 添加项目描述
                        if 'description' in project and project['description']:
                            # 转换Markdown为HTML
                            markdown_html = markdown.markdown(project['description'])
                            desc_container = BeautifulSoup(markdown_html, 'html.parser')
                            panel.append(desc_container)
                    
                    # 添加标签切换脚本
                    script = self.soup.new_tag('script')
                    script.string = '''
                        // 个人项目标签切换逻辑
                        document.addEventListener('DOMContentLoaded', function() {
                            const tabs = document.querySelectorAll('[id^="tab-project-"]');
                            const panels = document.querySelectorAll('[id^="panel-project-"]');
                            
                            tabs.forEach((tab, index) => {
                                tab.addEventListener('click', function() {
                                    // 激活当前标签
                                    tabs.forEach(t => {
                                        // 移除所有激活状态的类
                                        t.classList.remove('shadow-lg', 'transform', 'scale-105');
                                        t.classList.add('shadow-md');
                                    });
                                    // 激活当前标签
                                    tab.classList.add('shadow-lg', 'transform', 'scale-105');
                                    tab.classList.remove('shadow-md');
                                    
                                    // 显示当前面板
                                    panels.forEach(p => {
                                        p.classList.add('hidden');
                                        p.classList.remove('animate-fade-in');
                                    });
                                    panels[index].classList.remove('hidden');
                                    panels[index].classList.add('animate-fade-in');
                                });
                            });
                        });
                    '''
                    container.append(script)
                else:
                    # 只有一个个人项目，使用单一布局
                    for i, project in enumerate(projects):
                        # 创建项目卡片
                        card = self.soup.new_tag('div')
                        card['class'] = ['bg-white', 'rounded-xl', 'p-6', 'shadow-sm', 'card-hover']
                        content_container.append(card)
                        
                        # 添加项目信息
                        if 'name' in project and 'time' in project:
                            # 创建项目信息容器
                            info_container = self.soup.new_tag('div')
                            info_container['class'] = ['flex', 'flex-col', 'md:flex-row', 'justify-between', 'items-start', 'md:items-center', 'mb-4']
                            card.append(info_container)
                            
                            # 添加项目名称
                            name_div = self.soup.new_tag('div')
                            name_div['class'] = ['font-semibold', 'text-lg', 'mb-2', 'md:mb-0']
                            name_div.string = project['name']
                            info_container.append(name_div)
                            
                            # 添加项目时间
                            time_div = self.soup.new_tag('div')
                            time_div['class'] = ['text-primary', 'font-medium', 'mb-2', 'md:mb-0']
                            time_div.string = project['time']
                            info_container.append(time_div)
                        
                        # 添加项目描述
                        if 'description' in project and project['description']:
                            # 转换Markdown为HTML
                            markdown_html = markdown.markdown(project['description'])
                            desc_container = BeautifulSoup(markdown_html, 'html.parser')
                            card.append(desc_container)
            
            print("✓ 成功更新个人项目")
            return True
        except Exception as e:
            print(f"✗ 更新个人项目失败: {e}")
            return False
    
    def extract_skills(self):
        """提取专业技能信息"""
        skills = []
        
        # 提取专业技能
        skill_match = re.search(r'## 专业技能\n\n(.*?)## 自我评价', self.resume_content, re.DOTALL)
        if skill_match:
            skill_content = skill_match.group(1).strip()
            
            # 提取每条技能 - 使用更可靠的方法
            # 按行分割
            lines = skill_content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    # 移除开头的 '- '
                    skill = line[2:].strip()
                    if skill:
                        skills.append(skill)
        
        return skills
    
    def update_skills(self):
        """更新专业技能信息"""
        skills = self.extract_skills()
        
        if not skills:
            print("✗ 未提取到专业技能信息，不加载该部分")
            # 如果没有专业技能，移除网页中的专业技能部分
            skill_section = self.soup.find('section', id='skills')
            if skill_section:
                skill_section.decompose()
            # 移除导航栏中的专业技能链接
            nav = self.soup.find('nav')
            if nav:
                skill_link = nav.find('a', href='#skills')
                if skill_link:
                    skill_link.decompose()
            # 移除移动端导航栏中的专业技能链接
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                mobile_skill_link = mobile_nav.find('a', href='#skills')
                if mobile_skill_link:
                    mobile_skill_link.decompose()
            # 移除专业技能的注释标记
            for comment in self.soup.find_all(text=lambda text: isinstance(text, str) and '<!-- 专业技能 -->' in text):
                comment.extract()
            return True
        
        try:
            # 更新专业技能时间线
            skill_section = self.soup.find('section', id='skills')
            if skill_section:
                skill_container = skill_section.find('div', class_='space-y-6')
                if skill_container:
                    # 清空现有技能
                    skill_container.clear()
                    
                    # 添加新技能
                    icons = [
                        'fa-language', 'fa-line-chart', 'fa-pencil',
                        'fa-code', 'fa-magic', 'fa-html5',
                        'fa-film', 'fa-file-excel-o', 'fa-terminal'
                    ]
                    
                    for i, skill in enumerate(skills):
                        # 创建技能项
                        skill_div = self.soup.new_tag('div')
                        skill_div['class'] = ['flex', 'gap-4']
                        
                        # 创建图标部分
                        icon_div = self.soup.new_tag('div')
                        icon_div['class'] = ['relative']
                        
                        icon_container = self.soup.new_tag('div')
                        icon_container['class'] = ['w-8', 'h-8', 'bg-primary', 'rounded-full', 'flex', 'items-center', 'justify-center', 'text-white', 'z-10']
                        
                        icon = self.soup.new_tag('i')
                        icon['class'] = ['fa', icons[i % len(icons)]]
                        
                        icon_container.append(icon)
                        icon_div.append(icon_container)
                        
                        # 创建内容部分
                        content_div = self.soup.new_tag('div')
                        content_div['class'] = ['bg-white', 'p-4', 'rounded-lg', 'shadow-sm', 'flex-1', 'hover:shadow-md', 'transition-shadow', 'duration-300']
                        
                        content_p = self.soup.new_tag('p')
                        content_p['class'] = ['text-medium']
                        content_p.string = skill
                        
                        content_div.append(content_p)
                        
                        # 组合技能项
                        skill_div.append(icon_div)
                        skill_div.append(content_div)
                        
                        skill_container.append(skill_div)
            
            print("✓ 成功更新专业技能")
            return True
        except Exception as e:
            print(f"✗ 更新专业技能失败: {e}")
            return False
    
    def extract_self_evaluation(self):
        """提取自我评价信息"""
        evaluation = ""
        
        # 提取自我评价
        eval_match = re.search(r'## 自我评价\n\n(.*?)(?:<center>|$)', self.resume_content, re.DOTALL)
        if eval_match:
            evaluation = eval_match.group(1).strip()
        
        return evaluation
    
    def update_self_evaluation(self):
        """更新自我评价信息"""
        evaluation = self.extract_self_evaluation()
        
        if not evaluation:
            print("✗ 未提取到自我评价信息，不加载该部分")
            # 如果没有自我评价，移除网页中的自我评价部分
            eval_section = self.soup.find('section', id='self-evaluation')
            if eval_section:
                eval_section.decompose()
            # 移除导航栏中的自我评价链接
            nav = self.soup.find('nav')
            if nav:
                eval_link = nav.find('a', href='#self-evaluation')
                if eval_link:
                    eval_link.decompose()
            # 移除移动端导航栏中的自我评价链接
            mobile_nav = self.soup.find('div', id='mobile-menu')
            if mobile_nav:
                mobile_eval_link = mobile_nav.find('a', href='#self-evaluation')
                if mobile_eval_link:
                    mobile_eval_link.decompose()
            # 移除自我评价的注释标记
            for comment in self.soup.find_all(text=lambda text: isinstance(text, str) and '<!-- 自我评价 -->' in text):
                comment.extract()
            return True
        
        try:
            # 更新自我评价
            eval_section = self.soup.find('section', id='self-evaluation')
            if eval_section:
                eval_card = eval_section.find('div', class_='bg-white rounded-xl p-8 shadow-sm')
                if eval_card:
                    eval_p = eval_card.find('p', class_='text-medium')
                    if eval_p:
                        # 转换Markdown为HTML，处理HTML标签
                        markdown_html = markdown.markdown(evaluation)
                        eval_p.clear()
                        eval_p.append(BeautifulSoup(markdown_html, 'html.parser'))
            
            print("✓ 成功更新自我评价")
            return True
        except Exception as e:
            print(f"✗ 更新自我评价失败: {e}")
            return False
    
    def update_config_content(self):
        """更新配置相关的网页内容"""
        try:
            if not self.config:
                print("✗ 配置文件未加载，无法更新配置内容")
                return False
            
            # 更新网页标题标签
            if 'head_title' in self.config:
                title_elem = self.soup.find('title')
                if title_elem:
                    title_elem.string = self.config['head_title']
            
            # 更新页面标题（导航栏中的标题）
            if 'page_title' in self.config:
                nav_title_elem = self.soup.find('div', class_='text-xl font-bold text-primary')
                if nav_title_elem:
                    nav_title_elem.string = self.config['page_title']
            
            # 更新简历列表链接
            if 'resume_list_url' in self.config:
                # 查找简历列表按钮
                resume_list_buttons = self.soup.find_all('a')
                for button in resume_list_buttons:
                    if '简历文件列表' in button.get_text():
                        button['href'] = self.config['resume_list_url']
            
            # 更新招聘须知链接
            if 'recruitment_info_url' in self.config:
                # 查找招聘须知按钮
                recruitment_buttons = self.soup.find_all('a')
                for button in recruitment_buttons:
                    if '招聘须知' in button.get_text():
                        button['href'] = self.config['recruitment_info_url']
            
            # 更新简历下载链接
            if 'resume_pdf_url' in self.config:
                # 查找简历下载按钮
                download_buttons = self.soup.find_all('a')
                for button in download_buttons:
                    if '简历下载' in button.get_text() or '下载简历' in button.get_text():
                        button['href'] = self.config['resume_pdf_url']
            
            # 更新求职版简历下载链接
            if 'resume_job_pdf_url' in self.config:
                # 查找求职版简历下载按钮
                job_download_buttons = self.soup.find_all('a')
                for button in job_download_buttons:
                    if '求职版简历' in button.get_text() or '简历（求职）' in button.get_text():
                        button['href'] = self.config['resume_job_pdf_url']
            
            # 更新底部信息和最后更新时间
            # 查找底部信息容器
            footer_div = self.soup.find('div', class_='border-t border-gray-800 mt-8 pt-8 text-center text-gray-400')
            if footer_div:
                # 更新底部信息
                if 'footer_info' in self.config:
                    footer_p = footer_div.find('p')
                    if footer_p:
                        footer_p.string = self.config['footer_info']
                
                # 更新最后更新时间
                if 'last_updated' in self.config:
                    # 查找最后更新时间元素
                    update_time_elems = footer_div.find_all('p')
                    if len(update_time_elems) >= 2:
                        update_time_elem = update_time_elems[1]
                        update_time_elem.string = f"最后更新：{self.config['last_updated']}"
            
            print("✓ 成功更新配置内容")
            return True
        except Exception as e:
            print(f"✗ 更新配置内容失败: {e}")
            return False
    
    def save_html(self):
        """保存更新后的HTML文件"""
        try:
            # 获取HTML内容
            html_content = str(self.soup)
            
            # 移除所有部分的注释标记
            html_content = html_content.replace('<!-- 实习经历 -->', '')
            html_content = html_content.replace('<!-- 校园经历 -->', '')
            html_content = html_content.replace('<!-- 工作经历 -->', '')
            html_content = html_content.replace('<!-- 教育背景 -->', '')
            html_content = html_content.replace('<!-- 个人项目 -->', '')
            html_content = html_content.replace('<!-- 专业技能 -->', '')
            html_content = html_content.replace('<!-- 自我评价 -->', '')
            
            # 移除多余的空行
            import re
            html_content = re.sub(r'\n\s*\n', '\n\n', html_content)
            
            # 保存HTML文件
            with open(self.html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("✓ 成功保存HTML文件")
            return True
        except Exception as e:
            print(f"✗ 保存HTML文件失败: {e}")
            return False
    
    def update_all(self):
        """更新所有内容"""
        print("=== 开始更新简历网页 ===")
        
        # 加载文件
        if not self.load_resume():
            return False
        
        if not self.load_html():
            return False
        
        # 加载配置文件
        self.load_config()
        
        # 更新各个部分
        success = True
        
        if not self.update_personal_info():
            success = False
        
        if not self.update_education():
            success = False
        
        if not self.update_experience():
            success = False
        
        if not self.update_work_experience():
            success = False
        
        if not self.update_campus_experience():
            success = False
        
        if not self.update_projects():
            success = False
        
        if not self.update_skills():
            success = False
        
        if not self.update_self_evaluation():
            success = False
        
        if not self.update_config_content():
            success = False
        
        # 保存文件
        if success:
            # 先更新最后更新时间
            self.update_last_updated()
            # 重新加载配置文件以获取最新的最后更新时间
            self.load_config()
            # 再次更新配置内容，确保使用最新的最后更新时间
            self.update_config_content()
            # 保存HTML文件
            if self.save_html():
                print("\n🎉 简历网页更新成功！")
                return True
            else:
                return False
        else:
            print("\n❌ 简历网页更新失败！")
            return False

if __name__ == "__main__":
    # 定义文件路径
    resume_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resume', '简历.md')
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
    
    # 创建更新器实例
    updater = ResumeUpdater(resume_path, html_path)
    
    # 执行更新
    updater.update_all()
