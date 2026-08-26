# -*- coding: utf-8 -*-
import sys
import time
from ctypes import sizeof
from logging import exception
from sre_constants import RANGE
import pyvisa
import sys, time,os
os.chdir(sys.path[0]) 
sys.path.append("..")
from dongle.ch341 import ch341


SC85853_I2C_MASTER_ADDR = 0x6E
SC85853_I2C_SLAVE_ADDR = 0x6F


SC8583_I2C_SPEED = 400  # 100K

class SC85853(object):
	# ============================================================
	# FUNCTION INDEX — search here BEFORE writing any new function
	# ============================================================
	#
	# DEVICE_ID (0x00)      read_device_id
	#
	# INT_DEVICE0~3 (0x01~04)  read_por_flag / read_cp_switching_flag
	#                           read_vin_in_present_flag / read_vb_out_present_flag
	#                           read_vin_in_th_chg_en_flag / read_vb_out_th_chg_en_flag
	#                           read_vout_insert_flag / read_vout_th_rev_en_flag
	#                           read_vout_th_chg_en_flag / read_vusb_remove_flag
	#                           read_vext_remove_flag / read_vusb_insert_flag
	#                           read_vext_insert_flag / read_vusb_ovp_flag
	#                           read_vusb_drv_on_flag / read_vext_ovp_flag
	#                           read_vext_drv_on_flag / read_qb1_on_flag
	#                           read_qb2_on_flag / read_adc_done_flag
	#                           read_wd_timeout_flag / read_iin_ucp_rise_flag
	#                           read_tdie_reg_exit_flag / read_tdie_reg_active_flag
	#                           read_vbat_reg_active_flag / read_iin_reg_active_flag
	#  (all INT flags are read-only, read-to-clear)
	#
	# INT_FAULT0~3 (0x05~08)  read_iin_ocp_flag / read_iin_ucp_fall_flag
	#                          read_vin_ovp_flag / read_vb_out_ovp_flag
	#                          read_vout_ovp_flag / read_vbat_ovp_flag
	#                          read_c1a_short_flag / read_c1b_short_flag
	#                          read_c2a_short_flag / read_c2b_short_flag
	#                          read_c1a_open_flag / read_c1b_open_flag
	#                          read_c2a_open_flag / read_c2b_open_flag
	#                          read_pin_diag_fail_flag / read_pmid_errorhi_flag
	#                          read_pmid_errorlo_flag
	#                          read_bst1a_short_flag / read_bst1b_short_flag
	#                          read_bst2_short_flag / read_bst3a_short_flag
	#                          read_bst3b_short_flag / read_bst1a_open_flag
	#                          read_bst1b_open_flag / read_bst2_open_flag
	#
	# INT_FAULT4~6 (0x09~0B)  read_bst3a_open_flag / read_bst3b_open_flag
	#                          read_ext1_drv_short_flag / read_ext1_fet_open_flag
	#                          read_ext2_drv_short_flag / read_ext2_fet_open_flag
	#                          read_c1a_short_ph3_flag / read_c1b_short_ph3_flag
	#                          read_c2a_short_ph3_flag / read_c2b_short_ph3_flag
	#                          read_q5_short_flag / read_c1pa_c1pb_short_flag
	#                          read_q3a_short_flag / read_q3b_short_flag
	#                          read_conv_ocp_flag / read_vo12out_uvp_flag
	#                          read_c1p2out_uvp_flag / read_c1p2out_ovp_flag
	#                          read_ntc_flt_flag / read_tshut_flag
	#                          read_ss_fail_flag / read_ss_timeout_flag
	#
	# MASK_DEVICE0~3 (0x0C~0F) read_*_mask / write_*_mask (all interrupt masks)
	#                          (por, cp_switching, vin_in_present, vb_out_present,
	#                           vin_th_chg_en, vb_out_th_chg_en, vout_insert,
	#                           vout_th_rev_en, vout_th_chg_en, vusb_remove,
	#                           vext_remove, vusb_insert, vext_insert,
	#                           vusb_ovp, vusb_drv_on, vext_ovp, vext_drv_on,
	#                           qb1_on, qb2_on, adc_done, wd_timeout,
	#                           iin_ucp_rise, tdie_reg_exit, tdie_reg_active,
	#                           vbat_reg_active, iin_reg_active)
	#
	# MASK_FAULT0~3 (0x10~13) read_*_mask / write_*_mask (all fault masks)
	#                          (iin_ocp, iin_ucp_fall, vin_ovp, vb_out_ovp,
	#                           vout_ovp, vbat_ovp, pin_diag_fail, cfly_open,
	#                           cfly_short, bst_fail, pmid_errorhi, pmid_errorlo,
	#                           ext_drv1_short, ext_fet1_open, ext_drv2_short,
	#                           ext_fet2_open, conv_ocp, vo12out_uvp,
	#                           c1p2out_uvp, c1p2out_ovp, ntc_flt, tshut,
	#                           ss_fail, ss_timeout)
	#
	# STAT_DEVICE0 (0x14)   read_vb_out_present_stat / read_cp_switching_stat
	#                        read_vin_present_stat / read_vout_insert_stat
	#                        read_vout_th_rev_en_stat / read_vout_th_chg_en_stat
	#                        read_vin_th_chg_en_stat / read_vb_out_th_chg_en_stat
	#
	# STAT_DEVICE1 (0x15)   read_vext_ovp_stat / read_vext_drv_on_stat
	#                        read_vusb_insert_stat / read_vext_insert_stat
	#                        read_vusb_ovp_stat / read_vusb_drv_on_stat
	#                        read_qb1_on_stat / read_qb2_on_stat
	#
	# STAT_DEVICE2 (0x16)   read_adc_done_stat / read_wd_timeout_stat
	#                        read_iin_ucp_rise_stat / read_vout_ok_sw_avdd_stat
	#                        read_tdie_reg_active_stat / read_vbat_reg_active_stat
	#                        read_iin_reg_active_stat
	#
	# STAT_FAULT0 (0x17)    read_iin_ocp_stat / read_iin_ucp_fall_stat
	#                        read_vin_ovp_stat / read_vb_out_ovp_stat
	#                        read_vout_ovp_stat / read_vbat_ovp_stat
	#
	# STAT_FAULT1 (0x18)    read_c1a_short_stat / read_c1b_short_stat
	#                        read_c2a_short_stat / read_c2b_short_stat
	#                        read_c1a_open_stat / read_c1b_open_stat
	#                        read_c2a_open_stat / read_c2b_open_stat
	#
	# STAT_FAULT2 (0x19)    read_pin_diag_fail_stat
	#                        read_pmid_errorhi_stat / read_pmid_errorlo_stat
	#
	# STAT_FAULT3 (0x1A)    read_bst1a_short_stat / read_bst1b_short_stat
	#                        read_bst2_short_stat / read_bst3a_short_stat
	#                        read_bst3b_short_stat / read_bst1a_open_stat
	#                        read_bst1b_open_stat / read_bst2_open_stat
	#
	# STAT_FAULT4 (0x1B)    read_bst3a_open_stat / read_bst3b_open_stat
	#                        read_ext1_drv_short_stat / read_ext1_fet_open_stat
	#                        read_ext2_drv_short_stat / read_ext2_fet_open_stat
	#
	# STAT_FAULT5 (0x1C)    read_c1a_short_ph3_stat / read_c1b_short_ph3_stat
	#                        read_c2a_short_ph3_stat / read_c2b_short_ph3_stat
	#                        read_q5_short_stat / read_c1pa_c1pb_short_stat
	#                        read_q3a_short_stat / read_q3b_short_stat
	#
	# STAT_FAULT6 (0x1D)    read_conv_ocp_stat / read_vo12out_uvp_stat
	#                        read_c1p2out_uvp_stat / read_c1p2out_ovp_stat
	#                        read_ntc_flt_stat / read_tshut_stat
	#                        read_ss_fail_stat / read_ss_timeout_stat
	#
	# CTRL0 (0x1E)          read_cp_en / write_cp_en
	#                        read_qb1_ctrl2 / write_qb1_ctrl2
	#                        read_qb2_ctrl1 / write_qb2_ctrl1
	#                        read_qb2_ctrl2 / write_qb2_ctrl2
	#                        read_mode / write_mode
	#
	# CTRL1 (0x1F)          read_vin_present_dis / write_vin_present_dis
	#                        read_vb_out_present_dis / write_vb_out_present_dis
	#                        read_ss_timeout / write_ss_timeout
	#                        read_ss_fail_dis / write_ss_fail_dis
	#                        read_iin_ucp_fall_blanking_set / write_iin_ucp_fall_blanking_set
	#                        read_iin_ucp_en_method_sel / write_iin_ucp_en_method_sel
	#
	# CTRL2 (0x20)          read_vbus_ovp / write_vbus_ovp / read_vbus_ovp_dis / write_vbus_ovp_dis
	#                        read_vbus_ovp_dg_set / write_vbus_ovp_dg_set
	#                        read_freq_shift / write_freq_shift
	#                        read_fsw_set / write_fsw_set
	#                        read_sync_en / write_sync_en
	#
	# CTRL3 (0x21)          read_vbus2_ovp / write_vbus2_ovp / read_vbus2_ovp_dis / write_vbus2_ovp_dis
	#                        read_vbus2_ovp_dg_set / write_vbus2_ovp_dg_set
	#                        read_sync_role / write_sync_role
	#                        read_sync_out / write_sync_out
	#                        read_dual_config / write_dual_config
	#                        read_pmid_in_range_dis / write_pmid_in_range_dis
	#                        read_pmid_pd_en / write_pmid_pd_en
	#
	# CTRL4 (0x22)          read_reg_rst / write_reg_rst
	#                        read_standby_mode_set / write_standby_mode_set
	#                        read_wd_vusb_shutdown_en / write_wd_vusb_shutdown_en
	#                        read_wd_standby_en / write_wd_standby_en
	#                        read_wd_timeout_dis / write_wd_timeout_dis
	#                        read_wd_timeout / write_wd_timeout
	#                        read_vusb_shutdown_set / write_vusb_shutdown_set
	#
	# VUSB_CTRL (0x23)      read_vusb_ovp / write_vusb_ovp  (7.5V or 11~25V)
	#                        read_vusb_ovp_dis / write_vusb_ovp_dis
	#                        read_vusb_ovp_sel / write_vusb_ovp_sel
	#                        read_vusb_sw_ctrl1 / write_vusb_sw_ctrl1
	#                        read_vusb_sw_ctrl2 / write_vusb_sw_ctrl2
	#                        read_vusb_off_gate_ctrl / write_vusb_off_gate_ctrl
	#
	# VEXT_CTRL (0x24)      read_vext_ovp / write_vext_ovp  (7.5V or 11~25V)
	#                        read_vext_sw_ctrl1 / write_vext_sw_ctrl1
	#                        read_vext_sw_ctrl2 / write_vext_sw_ctrl2
	#                        read_vext_ovp_dis / write_vext_ovp_dis
	#                        read_acdrv_manual_en / write_acdrv_manual_en
	#                        read_vext_off_gate_ctrl / write_vext_off_gate_ctrl
	#
	# CTRL5 (0x25)          read_vusb_dischg_ctrl1 / write_vusb_dischg_ctrl1
	#                        read_vusb_dischg_ctrl2 / write_vusb_dischg_ctrl2
	#                        read_vext_dischg_ctrl1 / write_vext_dischg_ctrl1
	#                        read_vext_dischg_ctrl2 / write_vext_dischg_ctrl2
	#                        read_drv1_short_det_dis / write_drv1_short_det_dis
	#                        read_fet1_open_det_dis / write_fet1_open_det_dis
	#                        read_fet_open / write_fet_open
	#
	# CTRL6 (0x26)          read_drv2_short_det_dis / write_drv2_short_det_dis
	#                        read_fet2_open_det_dis / write_fet2_open_det_dis
	#                        read_cfly_short_det_ctrl / write_cfly_short_det_ctrl
	#                        read_vdc_chg_en_falling / write_vdc_chg_en_falling
	#                        read_vdc_chg_en_dg / write_vdc_chg_en_dg
	#
	# IIN_REG (0x27)        read_iin_reg / write_iin_reg           (mA, max 6000)
	#
	# VBAT_REG (0x28)       read_vbat_reg / write_vbat_reg         (V, 3.84~5.115)
	#
	# REG_CTRL (0x29)       read_iin_reg_dis / write_iin_reg_dis
	#                        read_vbat_reg_dis / write_vbat_reg_dis
	#                        read_iin_ucp_cfg / write_iin_ucp_cfg
	#                        read_tdie_reg_dis / write_tdie_reg_dis
	#                        read_iin_tdie_reg_interval / write_iin_tdie_reg_interval
	#                        read_tdie_reg / write_tdie_reg
	#
	# VBAT_OVP (0x2A)       read_vbat_ovp / write_vbat_ovp
	#
	# VIN_OVP (0x2B)        read_vin_ovp / write_vin_ovp / read_vin_ovp_dis / write_vin_ovp_dis
	#                        read_vin_pd_en / write_vin_pd_en
	#
	# VB_OUT_OVP (0x2C)     read_vb_out_ovp / write_vb_out_ovp
	#                        read_vb_out_ovp_dis / write_vb_out_ovp_dis
	#                        read_vb_out_pd_en / write_vb_out_pd_en
	#
	# IIN_OCP (0x2D)        read_iin_ocp / write_iin_ocp (mA, max 6375)
	#
	# VOUT/VDC_OVP (0x2E)   read_vout_ovp / write_vout_ovp / read_vout_ovp_dis / write_vout_ovp_dis
	#                        read_vdc_ovp / write_vdc_ovp
	#
	# C1P2OUT_OVP (0x2F)    read_c1p2out_ovp / write_c1p2out_ovp
	#                        read_c1p2out_ovp_dis / write_c1p2out_ovp_dis
	#                        read_c1p2out_ovp_blk / write_c1p2out_ovp_blk
	#                        read_c1p2out_ovp_dg / write_c1p2out_ovp_dg
	#
	# C1P2OUT_UVP (0x30)    read_c1p2out_uvp / write_c1p2out_uvp
	#                        read_c1p2out_uvp_dis / write_c1p2out_uvp_dis
	#                        read_c1p2out_uvp_blk / write_c1p2out_uvp_blk
	#                        read_c1p2out_uvp_dg / write_c1p2out_uvp_dg
	#
	# NTC_FLT (0x31)        read_ntc_flt / write_ntc_flt / read_ntc_flt_dis / write_ntc_flt_dis
	#
	# PROTECT_DIS (0x32)    read_iin_ocp_dis / write_iin_ocp_dis
	#                        read_pin_diag_fail_dis / write_pin_diag_fail_dis
	#                        read_cfly_open_dis / write_cfly_open_dis
	#                        read_cfly_short_dis / write_cfly_short_dis
	#                        read_bst_fail_dis / write_bst_fail_dis
	#                        read_tshut_dis / write_tshut_dis
	#                        read_vbat_ovp_dis / write_vbat_ovp_dis
	#                        read_vout_ovp_dis / write_vout_ovp_dis
	#
	# DEGLITCH_CTRL0 (0x33) read_iin_ocp_dg_set / write_iin_ocp_dg_set
	#                        read_iin_ucp_rise_dg_set / write_iin_ucp_rise_dg_set
	#                        read_iin_ucp_fall_dg_set / write_iin_ucp_fall_dg_set
	#
	# DEGLITCH_CTRL1 (0x34) read_vb_out_ovp_dg_set / write_vb_out_ovp_dg_set
	#
	# ADC_CTRL (0x35)       read_adc_en / write_adc_en
	#                        read_adc_rate / write_adc_rate
	#                        read_adc_freeze / write_adc_freeze
	#
	# ADC_FN_DISABLE (0x36) read_iin_adc_dis / write_iin_adc_dis
	#                        read_vin_adc_dis / write_vin_adc_dis
	#                        read_vb_out_adc_dis / write_vb_out_adc_dis
	#                        read_vusb_adc_dis / write_vusb_adc_dis
	#                        read_vext_adc_dis / write_vext_adc_dis
	#                        read_vout_adc_dis / write_vout_adc_dis
	#                        read_vbat_adc_dis / write_vbat_adc_dis
	#                        read_c1p_adc_dis / write_c1p_adc_dis
	#                        read_ntc_adc_dis / write_ntc_adc_dis
	#                        read_tdie_adc_dis / write_tdie_adc_dis
	#
	# ADC Readback (0x37~)  read_iin_adc / read_vin_adc / read_vb_out_adc
	#                        read_vusb_adc / read_vext_adc / read_vout_adc
	#                        read_vbat_adc / read_c1p_adc / read_ntc_adc
	#                        read_tdie_adc
	# (each now has freeze→read→unfreeze internally)
	#
	# Combined helpers:
	#   initial()            — efficiency test init (OVP→max, standby, watchdog off, protections disabled)
	#   read_all_fault_flags() — check all INT_FAULT0~6, raise RuntimeError with exact flag name
	#   disable_all_masks()    — write 0xFF to all mask registers (0x0C~0x13)
	#   cp_startup(qb, mode)   — start CP: set mode + QB + CP_EN in sequence
	#   cp_shutdown()          — write CP_EN=0
	# ============================================================
	def __init__(self):
		self.dongle = ch341()
		self.dongle.open()

	def speed(self, volt, kHz):
		self.dongle.config(volt, kHz)
		state = self.dongle.iic_read(SC85853_I2C_MASTER_ADDR, 0x0B, 1)
		if state[0] is True:
			print('I2C is connected')
		else:
			print('I2C is disconnected')
			raise Exception

	def reg_read(self, reg_addr):
		reg = self.dongle.iic_read(SC85853_I2C_MASTER_ADDR, reg_addr, 1)
		return reg[1]

	def reg_read_AUX(self, reg_addr):
		reg = self.dongle.iic_read(SC85853_I2C_SLAVE_ADDR, reg_addr, 1)
		return reg[1]
	

	def bits_read(self, reg_addr, bits_len, bits_start):
		reg_value = self.reg_read(reg_addr)
		reg_mask = 1
		for index in range(bits_len - 1):
			reg_mask = (reg_mask << 1) + 1
		reg_mask = reg_mask << bits_start
		bits_value = (reg_value & reg_mask) >> bits_start
		return bits_value

	def bits_read_AUX(self, reg_addr, bits_len, bits_start):
		reg_value = self.reg_read_AUX(reg_addr)
		reg_mask = 1
		for index in range(bits_len - 1):
			reg_mask = (reg_mask << 1) + 1
		reg_mask = reg_mask << bits_start
		bits_value = (reg_value & reg_mask) >> bits_start
		return bits_value

	def bits_write(self, bits_in, reg_addr, bits_len, bits_start):
		reg_read = self.dongle.iic_read(SC85853_I2C_MASTER_ADDR, reg_addr, 1)
		reg_old = reg_read[1]
		reg_mask = 1
		for index in range(bits_len-1):
			reg_mask = (reg_mask << 1) + 1
		reg_mask = reg_mask << bits_start
		reg_new = (reg_old & (~reg_mask)) + ((bits_in << bits_start) & reg_mask)
		self.dongle.iic_write(SC85853_I2C_MASTER_ADDR, reg_addr, reg_new)
	

	def bits_write_AUX(self, bits_in, reg_addr, bits_len, bits_start):
		reg_read = self.dongle.iic_read(SC85853_I2C_SLAVE_ADDR, reg_addr, 1)
		reg_old = reg_read[1]
		reg_mask = 1
		for index in range(bits_len-1):
			reg_mask = (reg_mask << 1) + 1
		reg_mask = reg_mask << bits_start
		reg_new = (reg_old & (~reg_mask)) + ((bits_in << bits_start) & reg_mask)
		self.dongle.iic_write(SC85853_I2C_SLAVE_ADDR, reg_addr, reg_new)


	def Group_bytes_write_in(self,input_str):

		groups = input_str.split(';')
		result = []
		
		for group in groups:
			if not group.strip():
				continue

			parts = group.split()
			if len(parts) < 2:
				continue
				
			first_part = parts[0].strip().upper()
			second_part = parts[1].strip().upper()
			

			if first_part.startswith('X'):
				first_hex = first_part[1:]  
			elif first_part.startswith('0X'):
				first_hex = first_part[2:]  
			else:
				first_hex = first_part 
				
			# 确保十六进制值长度为2
			if len(first_hex) == 1:
				first_hex = '0' + first_hex
			
	
			if second_part.startswith('0X'):
				second_str = second_part[2:]  
			else:
				second_str = second_part
				

			if len(second_str) == 1:
				second_str = '0' + second_str
				
			result.append((first_hex, second_str))
		
		for tp in result:
			time.sleep(0.05)
			self.write_byte(tp)
		return

	def write_byte(self,tp):
		self.bits_write(int(tp[1],16),int(tp[0],16),8,0)
		time.sleep(0.1)

	# ==================== SC85853 Register Operation Functions ====================

	def read_device_id(self):
		"""Read Device ID (8 bits of reg 0x00)"""
		return self.bits_read(0x00, 8, 0)

	def read_por_flag(self):
		"""
		Read INT_DEVICE0 (0x01) BIT7: POR_FLAG
		Note: Interrupt flag register — read to clear
		Returns:
			0: Normal
			1: POR signal rising edge detected
		"""
		return self.bits_read(0x01, 1, 7)

	# INT_DEVICE0 (0x01)
	def read_cp_switching_flag(self):
		"""Read INT_DEVICE0 (0x01) BIT6: CP_SWITCHING_FLAG
		Note: Read to clear | 0: Normal | 1: CP_SWITCHING_STAT signal rising edge detected"""
		return self.bits_read(0x01, 1, 6)

	def read_vin_in_present_flag(self):
		"""Read INT_DEVICE0 (0x01) BIT5: VIN_IN_PRESENT_FLAG
		Note: Read to clear | 0: Normal | 1: VIN_IN_PRESENT_STAT signal rising edge detected"""
		return self.bits_read(0x01, 1, 5)

	def read_vb_out_present_flag(self):
		"""Read INT_DEVICE0 (0x01) BIT4: VB_OUT_PRESENT_FLAG
		Note: Read to clear | 0: Normal | 1: VB_OUT_PRESENT_STAT signal rising edge detected"""
		return self.bits_read(0x01, 1, 4)

	def read_vin_in_th_chg_en_flag(self):
		"""Read INT_DEVICE0 (0x01) BIT3: VIN_IN_TH_CHG_EN_FLAG
		Note: Read to clear | 0: Normal | 1: VIN_IN_TH_CHG_EN_STAT signal falling edge detected"""
		return self.bits_read(0x01, 1, 3)

	def read_vb_out_th_chg_en_flag(self):
		"""Read INT_DEVICE0 (0x01) BIT2: VB_OUT_TH_CHG_EN_FLAG
		Note: Read to clear | 0: Normal | 1: VB_OUT_TH_CHG_EN_STAT signal falling edge detected"""
		return self.bits_read(0x01, 1, 2)

	# INT_DEVICE1 (0x02) - flags
	def read_vout_insert_flag(self):
		"""Read INT_DEVICE1 (0x02) BIT7: VOUT_INSERT_FLAG
		Note: Read to clear | 0: Normal | 1: VOUT_INSERT_STA signal rising edge detected"""
		return self.bits_read(0x02, 1, 7)

	def read_vout_th_rev_en_flag(self):
		"""Read INT_DEVICE1 (0x02) BIT6: VOUT_TH_REV_EN_FLAG
		Note: Read to clear | 0: Normal | 1: VOUT_TH_REV_EN_STAT signal falling edge detected"""
		return self.bits_read(0x02, 1, 6)

	def read_vout_th_chg_en_flag(self):
		"""Read INT_DEVICE1 (0x02) BIT5: VOUT_TH_CHG_EN_FLAG
		Note: Read to clear | 0: Normal | 1: VOUT_TH_CHG_EN_STAT signal falling edge detected"""
		return self.bits_read(0x02, 1, 5)

	def read_vusb_remove_flag(self):
		"""Read INT_DEVICE1 (0x02) BIT4: VUSB_REMOVE_FLAG
		Note: Read to clear | 0: Normal | 1: VUSB_REMOVE_STAT signal rising edge detected"""
		return self.bits_read(0x02, 1, 4)

	def read_vext_remove_flag(self):
		"""Read INT_DEVICE1 (0x02) BIT3: VEXT_REMOVE_FLAG
		Note: Read to clear | 0: Normal | 1: VEXT_REMOVE_STAT signal rising edge detected"""
		return self.bits_read(0x02, 1, 3)

	def read_vusb_insert_flag(self):
		"""Read INT_DEVICE1 (0x02) BIT2: VUSB_INSERT_FLAG
		Note: Read to clear | 0: Normal | 1: VUSB_INSERT_STAT signal rising edge detected"""
		return self.bits_read(0x02, 1, 2)

	def read_vext_insert_flag(self):
		"""Read INT_DEVICE1 (0x02) BIT1: VEXT_INSERT_FLAG
		Note: Read to clear | 0: Normal | 1: VEXT_INSERT_STAT signal rising edge detected"""
		return self.bits_read(0x02, 1, 1)

	# INT_DEVICE2 (0x03) - flags
	def read_vusb_ovp_flag(self):
		"""Read INT_DEVICE2 (0x03) BIT7: VUSB_OVP_FLAG
		Note: Read to clear | 0: Normal | 1: VUSB_OVP_STAT signal rising edge detected"""
		return self.bits_read(0x03, 1, 7)

	def read_vusb_drv_on_flag(self):
		"""Read INT_DEVICE2 (0x03) BIT6: VUSB_DRV_ON_FLAG
		Note: Read to clear | 0: Normal | 1: VUSB_DRV_ON_STAT signal rising edge detected"""
		return self.bits_read(0x03, 1, 6)

	def read_vext_ovp_flag(self):
		"""Read INT_DEVICE2 (0x03) BIT5: VEXT_OVP_FLAG
		Note: Read to clear | 0: Normal | 1: VEXT_OVP_STAT signal rising edge detected"""
		return self.bits_read(0x03, 1, 5)

	def read_vext_drv_on_flag(self):
		"""Read INT_DEVICE2 (0x03) BIT4: VEXT_DRV_ON_FLAG
		Note: Read to clear | 0: Normal | 1: VEXT_DRV_ON_STAT signal rising edge detected"""
		return self.bits_read(0x03, 1, 4)

	def read_qb1_on_flag(self):
		"""Read INT_DEVICE2 (0x03) BIT3: QB1_ON_FLAG
		Note: Read to clear | 0: Normal | 1: QB1_ON_STAT signal rising edge detected"""
		return self.bits_read(0x03, 1, 3)

	def read_qb2_on_flag(self):
		"""Read INT_DEVICE2 (0x03) BIT2: QB2_ON_FLAG
		Note: Read to clear | 0: Normal | 1: QB2_ON_STAT signal rising edge detected"""
		return self.bits_read(0x03, 1, 2)

	# INT_DEVICE3 (0x04) - flags
	def read_adc_done_flag(self):
		"""Read INT_DEVICE3 (0x04) BIT7: ADC_DONE_FLAG
		Note: Read to clear | 0: Normal | 1: ADC_DONE_STAT signal rising edge detected"""
		return self.bits_read(0x04, 1, 7)

	def read_wd_timeout_flag(self):
		"""Read INT_DEVICE3 (0x04) BIT6: WD_TIMEOUT_FLAG
		Note: Read to clear | 0: Normal | 1: WD_TIMEOUT_STAT signal rising edge detected"""
		return self.bits_read(0x04, 1, 6)

	def read_iin_ucp_rise_flag(self):
		"""Read INT_DEVICE3 (0x04) BIT5: IIN_UCP_RISE_FLAG
		Note: Read to clear | 0: Normal | 1: IIN_UCP_STAT signal rising edge detected"""
		return self.bits_read(0x04, 1, 5)

	def read_tdie_reg_exit_flag(self):
		"""Read INT_DEVICE3 (0x04) BIT4: TDIE_REG_EXIT_FLAG
		Note: Read to clear | 0: Normal | 1: TDIE_REG_ACTIVE_STAT signal falling edge detected"""
		return self.bits_read(0x04, 1, 4)

	def read_tdie_reg_active_flag(self):
		"""Read INT_DEVICE3 (0x04) BIT3: TDIE_REG_ACTIVE_FLAG
		Note: Read to clear | 0: Normal | 1: TDIE_REG_ACTIVE_STAT signal rising edge detected"""
		return self.bits_read(0x04, 1, 3)

	def read_vbat_reg_active_flag(self):
		"""Read INT_DEVICE3 (0x04) BIT2: VBAT_REG_ACTIVE_FLAG
		Note: Read to clear | 0: Normal | 1: VBAT_REG_ACTIVE_STAT signal rising edge detected"""
		return self.bits_read(0x04, 1, 2)

	def read_iin_reg_active_flag(self):
		"""Read INT_DEVICE3 (0x04) BIT0: IIN_REG_ACTIVE_FLAG
		Note: Read to clear | 0: Normal | 1: IIN_REG_ACTIVE_STAT signal rising edge detected"""
		return self.bits_read(0x04, 1, 0)

	# INT_FAULT0 (0x05) - flags
	def read_iin_ocp_flag(self):
		"""Read INT_FAULT0 (0x05) BIT7: IIN_OCP_FLAG
		Note: Read to clear | 0: Normal | 1: IIN_OCP_STAT signal rising edge detected"""
		return self.bits_read(0x05, 1, 7)

	def read_iin_ucp_fall_flag(self):
		"""Read INT_FAULT0 (0x05) BIT6: IIN_UCP_FALL_FLAG
		Note: Read to clear | 0: Normal | 1: IIN_UCP_FALL_STAT signal rising edge detected"""
		return self.bits_read(0x05, 1, 6)

	def read_vin_ovp_flag(self):
		"""Read INT_FAULT0 (0x05) BIT5: VIN_OVP_FLAG
		Note: Read to clear | 0: Normal | 1: VIN_OVP_STAT signal rising edge detected"""
		return self.bits_read(0x05, 1, 5)

	def read_vb_out_ovp_flag(self):
		"""Read INT_FAULT0 (0x05) BIT4: VB_OUT_OVP_FLAG
		Note: Read to clear | 0: Normal | 1: VB_OUT_OVP_STAT signal rising edge detected"""
		return self.bits_read(0x05, 1, 4)

	def read_vout_ovp_flag(self):
		"""Read INT_FAULT0 (0x05) BIT1: VOUT_OVP_FLAG
		Note: Read to clear | 0: Normal | 1: VOUT_OVP_STAT signal rising edge detected"""
		return self.bits_read(0x05, 1, 1)

	def read_vbat_ovp_flag(self):
		"""Read INT_FAULT0 (0x05) BIT0: VBAT_OVP_FLAG
		Note: Read to clear | 0: Normal | 1: VBAT_OVP_STAT signal rising edge detected"""
		return self.bits_read(0x05, 1, 0)

	# INT_FAULT1 (0x06) - flags
	def read_c1a_short_flag(self):
		"""Read INT_FAULT1 (0x06) BIT7: C1A_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: C1A_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x06, 1, 7)

	def read_c1b_short_flag(self):
		"""Read INT_FAULT1 (0x06) BIT6: C1B_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: C1B_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x06, 1, 6)

	def read_c2a_short_flag(self):
		"""Read INT_FAULT1 (0x06) BIT5: C2A_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: C2A_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x06, 1, 5)

	def read_c2b_short_flag(self):
		"""Read INT_FAULT1 (0x06) BIT4: C2B_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: C2B_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x06, 1, 4)

	def read_c1a_open_flag(self):
		"""Read INT_FAULT1 (0x06) BIT3: C1A_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: C1A_OPEN_STAT signal rising edge detected"""
		return self.bits_read(0x06, 1, 3)

	def read_c1b_open_flag(self):
		"""Read INT_FAULT1 (0x06) BIT2: C1B_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: C1B_OPEN_STAT signal rising edge detected"""
		return self.bits_read(0x06, 1, 2)

	def read_c2a_open_flag(self):
		"""Read INT_FAULT1 (0x06) BIT1: C2A_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: C2A_OPEN_STAT signal rising edge detected"""
		return self.bits_read(0x06, 1, 1)

	def read_c2b_open_flag(self):
		"""Read INT_FAULT1 (0x06) BIT0: C2B_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: C2B_OPEN_STAT signal rising edge detected"""
		return self.bits_read(0x06, 1, 0)

	# INT_FAULT2 (0x07) - flags
	def read_pin_diag_fail_flag(self):
		"""Read INT_FAULT2 (0x07) BIT7: PIN_DIAG_FAIL_FLAG
		Note: Read to clear | 0: Normal | 1: PIN_DIAG_FAIL_STAT signal rising edge detected"""
		return self.bits_read(0x07, 1, 7)

	def read_pmid_errorhi_flag(self):
		"""Read INT_FAULT2 (0x07) BIT1: PMID_ERRORHI_FLAG
		Note: Read to clear | 0: Normal | 1: PMID_ERRORHI_STAT signal rising edge detected"""
		return self.bits_read(0x07, 1, 1)

	def read_pmid_errorlo_flag(self):
		"""Read INT_FAULT2 (0x07) BIT0: PMID_ERRORLO_FLAG
		Note: Read to clear | 0: Normal | 1: PMID_ERRORLO_STAT signal rising edge detected"""
		return self.bits_read(0x07, 1, 0)

	# INT_FAULT3 (0x08) - flags
	def read_bst1a_short_flag(self):
		"""Read INT_FAULT3 (0x08) BIT7: BST1A_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: BST1A_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x08, 1, 7)

	def read_bst1b_short_flag(self):
		"""Read INT_FAULT3 (0x08) BIT6: BST1B_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: BST1B_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x08, 1, 6)

	def read_bst2_short_flag(self):
		"""Read INT_FAULT3 (0x08) BIT5: BST2_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: BST2_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x08, 1, 5)

	def read_bst3a_short_flag(self):
		"""Read INT_FAULT3 (0x08) BIT4: BST3A_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: BST3A_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x08, 1, 4)

	def read_bst3b_short_flag(self):
		"""Read INT_FAULT3 (0x08) BIT3: BST3B_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: BST3B_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x08, 1, 3)

	def read_bst1a_open_flag(self):
		"""Read INT_FAULT3 (0x08) BIT2: BST1A_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: BST1A_OPEN_STAT signal rising edge detected"""
		return self.bits_read(0x08, 1, 2)

	def read_bst1b_open_flag(self):
		"""Read INT_FAULT3 (0x08) BIT1: BST1B_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: BST1B_OPEN_STAT signal rising edge detected"""
		return self.bits_read(0x08, 1, 1)

	def read_bst2_open_flag(self):
		"""Read INT_FAULT3 (0x08) BIT0: BST2_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: BST2_OPEN_STAT signal rising edge detected"""
		return self.bits_read(0x08, 1, 0)

	# INT_FAULT4 (0x09) - flags
	def read_bst3a_open_flag(self):
		"""Read INT_FAULT4 (0x09) BIT7: BST3A_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: BST3A_OPEN_STAT signal rising edge detected"""
		return self.bits_read(0x09, 1, 7)

	def read_bst3b_open_flag(self):
		"""Read INT_FAULT4 (0x09) BIT6: BST3B_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: BST3B_OPEN_STAT signal rising edge detected"""
		return self.bits_read(0x09, 1, 6)

	def read_ext1_drv_short_flag(self):
		"""Read INT_FAULT4 (0x09) BIT3: EXT1_DRV_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: EXT1_DRV_SHORT signal rising edge detected"""
		return self.bits_read(0x09, 1, 3)

	def read_ext1_fet_open_flag(self):
		"""Read INT_FAULT4 (0x09) BIT2: EXT1_FET_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: EXT1_FET_OPEN signal rising edge detected"""
		return self.bits_read(0x09, 1, 2)

	def read_ext2_drv_short_flag(self):
		"""Read INT_FAULT4 (0x09) BIT1: EXT2_DRV_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: EXT2_DRV_SHORT signal rising edge detected"""
		return self.bits_read(0x09, 1, 1)

	def read_ext2_fet_open_flag(self):
		"""Read INT_FAULT4 (0x09) BIT0: EXT2_FET_OPEN_FLAG
		Note: Read to clear | 0: Normal | 1: EXT2_FET_OPEN signal rising edge detected"""
		return self.bits_read(0x09, 1, 0)

	# INT_FAULT5 (0x0A) - flags
	def read_c1a_short_ph3_flag(self):
		"""Read INT_FAULT5 (0x0A) BIT7: C1A_SHORT_PH3_FLAG
		Note: Read to clear | 0: Normal | 1: C1A_SHORT_PH3_STAT signal rising edge detected"""
		return self.bits_read(0x0A, 1, 7)

	def read_c1b_short_ph3_flag(self):
		"""Read INT_FAULT5 (0x0A) BIT6: C1B_SHORT_PH3_FLAG
		Note: Read to clear | 0: Normal | 1: C1B_SHORT_PH3_STAT signal rising edge detected"""
		return self.bits_read(0x0A, 1, 6)

	def read_c2a_short_ph3_flag(self):
		"""Read INT_FAULT5 (0x0A) BIT5: C2A_SHORT_PH3_FLAG
		Note: Read to clear | 0: Normal | 1: C2A_SHORT_PH3_STAT signal rising edge detected"""
		return self.bits_read(0x0A, 1, 5)

	def read_c2b_short_ph3_flag(self):
		"""Read INT_FAULT5 (0x0A) BIT4: C2B_SHORT_PH3_FLAG
		Note: Read to clear | 0: Normal | 1: C2B_SHORT_PH3_STAT signal rising edge detected"""
		return self.bits_read(0x0A, 1, 4)

	def read_q5_short_flag(self):
		"""Read INT_FAULT5 (0x0A) BIT3: Q5_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: Q5_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x0A, 1, 3)

	def read_c1pa_c1pb_short_flag(self):
		"""Read INT_FAULT5 (0x0A) BIT2: C1PA_C1PB_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: C1PA_C1PB_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x0A, 1, 2)

	def read_q3a_short_flag(self):
		"""Read INT_FAULT5 (0x0A) BIT1: Q3A_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: Q3A_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x0A, 1, 1)

	def read_q3b_short_flag(self):
		"""Read INT_FAULT5 (0x0A) BIT0: Q3B_SHORT_FLAG
		Note: Read to clear | 0: Normal | 1: Q3B_SHORT_STAT signal rising edge detected"""
		return self.bits_read(0x0A, 1, 0)

	# INT_FAULT6 (0x0B) - flags
	def read_conv_ocp_flag(self):
		"""Read INT_FAULT6 (0x0B) BIT7: CONV_OCP_FLAG
		Note: Read to clear | 0: Normal | 1: CONV_OCP_STAT signal rising edge detected"""
		return self.bits_read(0x0B, 1, 7)

	def read_vo12out_uvp_flag(self):
		"""Read INT_FAULT6 (0x0B) BIT6: VO12OUT_UVP_FLAG
		Note: Read to clear | 0: Normal | 1: VO12OUT_UVP_STAT signal rising edge detected"""
		return self.bits_read(0x0B, 1, 6)

	def read_c1p2out_uvp_flag(self):
		"""Read INT_FAULT6 (0x0B) BIT5: C1P2OUT_UVP_FLAG
		Note: Read to clear | 0: Normal | 1: PMID2OUT_UVP_STAT signal rising edge detected"""
		return self.bits_read(0x0B, 1, 5)

	def read_c1p2out_ovp_flag(self):
		"""Read INT_FAULT6 (0x0B) BIT4: C1P2OUT_OVP_FLAG
		Note: Read to clear | 0: Normal | 1: PMID2OUT_OVP_STAT signal rising edge detected"""
		return self.bits_read(0x0B, 1, 4)

	def read_ntc_flt_flag(self):
		"""Read INT_FAULT6 (0x0B) BIT3: NTC_FLT_FLAG
		Note: Read to clear | 0: Normal | 1: NTC_FLT_STAT signal rising edge detected"""
		return self.bits_read(0x0B, 1, 3)

	def read_tshut_flag(self):
		"""Read INT_FAULT6 (0x0B) BIT2: TSHUT_FLAG
		Note: Read to clear | 0: Normal | 1: TSHUT_STAT signal rising edge detected"""
		return self.bits_read(0x0B, 1, 2)

	def read_ss_fail_flag(self):
		"""Read INT_FAULT6 (0x0B) BIT1: SS_FAIL_FLAG
		Note: Read to clear | 0: Normal | 1: SS_FAIL_STAT signal rising edge detected"""
		return self.bits_read(0x0B, 1, 1)

	def read_ss_timeout_flag(self):
		"""Read INT_FAULT6 (0x0B) BIT0: SS_TIMEOUT_FLAG
		Note: Read to clear | 0: Normal | 1: SS_TIMEOUT_STAT signal rising edge detected"""
		return self.bits_read(0x0B, 1, 0)


	# ==================== MASK_DEVICE0 (0x0C) ====================

	def read_por_mask(self):
		"""
		Read MASK_DEVICE0 (0x0C) BIT7: POR_MASK
		Note: 0 = Not Masked (interrupt enabled) | 1 = Masked (interrupt disabled)
		"""
		return self.bits_read(0x0C, 1, 7)

	def write_por_mask(self, value):
		"""
		Write MASK_DEVICE0 (0x0C) BIT7: POR_MASK
		Args:
			value: 0 = Not Masked | 1 = Masked
		Note: Only BIT7 is modified; other bits preserved via read-modify-write
		"""
		self.bits_write(value, 0x0C, 1, 7)

	def read_cp_switching_mask(self):
		"""
		Read MASK_DEVICE0 (0x0C) BIT6: CP_SWITCHING_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0C, 1, 6)

	def write_cp_switching_mask(self, value):
		"""
		Write MASK_DEVICE0 (0x0C) BIT6: CP_SWITCHING_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0C, 1, 6)

	def read_vin_in_present_mask(self):
		"""
		Read MASK_DEVICE0 (0x0C) BIT5: VIN_IN_PRESENT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0C, 1, 5)

	def write_vin_in_present_mask(self, value):
		"""
		Write MASK_DEVICE0 (0x0C) BIT5: VIN_IN_PRESENT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0C, 1, 5)

	def read_vb_out_present_mask(self):
		"""
		Read MASK_DEVICE0 (0x0C) BIT4: VB_OUT_PRESENT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0C, 1, 4)

	def write_vb_out_present_mask(self, value):
		"""
		Write MASK_DEVICE0 (0x0C) BIT4: VB_OUT_PRESENT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0C, 1, 4)

	def read_vin_th_chg_en_mask(self):
		"""
		Read MASK_DEVICE0 (0x0C) BIT3: VIN_TH_CHG_EN_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0C, 1, 3)

	def write_vin_th_chg_en_mask(self, value):
		"""
		Write MASK_DEVICE0 (0x0C) BIT3: VIN_TH_CHG_EN_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0C, 1, 3)

	def read_vb_out_th_chg_en_mask(self):
		"""
		Read MASK_DEVICE0 (0x0C) BIT2: VB_OUT_TH_CHG_EN_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0C, 1, 2)

	def write_vb_out_th_chg_en_mask(self, value):
		"""
		Write MASK_DEVICE0 (0x0C) BIT2: VB_OUT_TH_CHG_EN_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0C, 1, 2)



	# ==================== MASK_DEVICE1 (0x0D) ====================

	def read_vout_insert_mask(self):
		"""
		Read MASK_DEVICE1 (0x0D) BIT7: VOUT_INSERT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0D, 1, 7)

	def write_vout_insert_mask(self, value):
		"""
		Write MASK_DEVICE1 (0x0D) BIT7: VOUT_INSERT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0D, 1, 7)

	def read_vout_th_rev_en_mask(self):
		"""
		Read MASK_DEVICE1 (0x0D) BIT6: VOUT_TH_REV_EN_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0D, 1, 6)

	def write_vout_th_rev_en_mask(self, value):
		"""
		Write MASK_DEVICE1 (0x0D) BIT6: VOUT_TH_REV_EN_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0D, 1, 6)

	def read_vout_th_chg_en_mask(self):
		"""
		Read MASK_DEVICE1 (0x0D) BIT5: VOUT_TH_CHG_EN_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0D, 1, 5)

	def write_vout_th_chg_en_mask(self, value):
		"""
		Write MASK_DEVICE1 (0x0D) BIT5: VOUT_TH_CHG_EN_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0D, 1, 5)

	def read_vusb_remove_mask(self):
		"""
		Read MASK_DEVICE1 (0x0D) BIT4: VUSB_REMOVE_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0D, 1, 4)

	def write_vusb_remove_mask(self, value):
		"""
		Write MASK_DEVICE1 (0x0D) BIT4: VUSB_REMOVE_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0D, 1, 4)

	def read_vext_remove_mask(self):
		"""
		Read MASK_DEVICE1 (0x0D) BIT3: VEXT_REMOVE_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0D, 1, 3)

	def write_vext_remove_mask(self, value):
		"""
		Write MASK_DEVICE1 (0x0D) BIT3: VEXT_REMOVE_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0D, 1, 3)

	def read_vusb_insert_mask(self):
		"""
		Read MASK_DEVICE1 (0x0D) BIT2: VUSB_INSERT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0D, 1, 2)

	def write_vusb_insert_mask(self, value):
		"""
		Write MASK_DEVICE1 (0x0D) BIT2: VUSB_INSERT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0D, 1, 2)

	def read_vext_insert_mask(self):
		"""
		Read MASK_DEVICE1 (0x0D) BIT1: VEXT_INSERT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0D, 1, 1)

	def write_vext_insert_mask(self, value):
		"""
		Write MASK_DEVICE1 (0x0D) BIT1: VEXT_INSERT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0D, 1, 1)




	# ==================== MASK_DEVICE2 (0x0E) ====================

	def read_vusb_ovp_mask(self):
		"""
		Read MASK_DEVICE2 (0x0E) BIT7: VUSB_OVP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0E, 1, 7)

	def write_vusb_ovp_mask(self, value):
		"""
		Write MASK_DEVICE2 (0x0E) BIT7: VUSB_OVP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0E, 1, 7)

	def read_vusb_drv_on_mask(self):
		"""
		Read MASK_DEVICE2 (0x0E) BIT6: VUSB_DRV_ON_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0E, 1, 6)

	def write_vusb_drv_on_mask(self, value):
		"""
		Write MASK_DEVICE2 (0x0E) BIT6: VUSB_DRV_ON_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0E, 1, 6)

	def read_vext_ovp_mask(self):
		"""
		Read MASK_DEVICE2 (0x0E) BIT5: VEXT_OVP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0E, 1, 5)

	def write_vext_ovp_mask(self, value):
		"""
		Write MASK_DEVICE2 (0x0E) BIT5: VEXT_OVP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0E, 1, 5)

	def read_vext_drv_on_mask(self):
		"""
		Read MASK_DEVICE2 (0x0E) BIT4: VEXT_DRV_ON_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0E, 1, 4)

	def write_vext_drv_on_mask(self, value):
		"""
		Write MASK_DEVICE2 (0x0E) BIT4: VEXT_DRV_ON_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0E, 1, 4)

	def read_qb1_on_mask(self):
		"""
		Read MASK_DEVICE2 (0x0E) BIT3: QB1_ON_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0E, 1, 3)

	def write_qb1_on_mask(self, value):
		"""
		Write MASK_DEVICE2 (0x0E) BIT3: QB1_ON_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0E, 1, 3)

	def read_qb2_on_mask(self):
		"""
		Read MASK_DEVICE2 (0x0E) BIT2: QB2_ON_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0E, 1, 2)

	def write_qb2_on_mask(self, value):
		"""
		Write MASK_DEVICE2 (0x0E) BIT2: QB2_ON_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0E, 1, 2)




	# ==================== MASK_DEVICE3 (0x0F) ====================

	def read_adc_done_mask(self):
		"""
		Read MASK_DEVICE3 (0x0F) BIT7: ADC_DONE_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0F, 1, 7)

	def write_adc_done_mask(self, value):
		"""
		Write MASK_DEVICE3 (0x0F) BIT7: ADC_DONE_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0F, 1, 7)

	def read_wd_timeout_mask(self):
		"""
		Read MASK_DEVICE3 (0x0F) BIT6: WD_TIMEOUT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0F, 1, 6)

	def write_wd_timeout_mask(self, value):
		"""
		Write MASK_DEVICE3 (0x0F) BIT6: WD_TIMEOUT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0F, 1, 6)

	def read_iin_ucp_rise_mask(self):
		"""
		Read MASK_DEVICE3 (0x0F) BIT5: IIN_UCP_RISE_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0F, 1, 5)

	def write_iin_ucp_rise_mask(self, value):
		"""
		Write MASK_DEVICE3 (0x0F) BIT5: IIN_UCP_RISE_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0F, 1, 5)

	def read_tdie_reg_exit_mask(self):
		"""
		Read MASK_DEVICE3 (0x0F) BIT4: TDIE_REG_EXIT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0F, 1, 4)

	def write_tdie_reg_exit_mask(self, value):
		"""
		Write MASK_DEVICE3 (0x0F) BIT4: TDIE_REG_EXIT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0F, 1, 4)

	def read_tdie_reg_active_mask(self):
		"""
		Read MASK_DEVICE3 (0x0F) BIT3: TDIE_REG_ACTIVE_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0F, 1, 3)

	def write_tdie_reg_active_mask(self, value):
		"""
		Write MASK_DEVICE3 (0x0F) BIT3: TDIE_REG_ACTIVE_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0F, 1, 3)

	def read_vbat_reg_active_mask(self):
		"""
		Read MASK_DEVICE3 (0x0F) BIT2: VBAT_REG_ACTIVE_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0F, 1, 2)

	def write_vbat_reg_active_mask(self, value):
		"""
		Write MASK_DEVICE3 (0x0F) BIT2: VBAT_REG_ACTIVE_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0F, 1, 2)


	def read_iin_reg_active_mask(self):
		"""
		Read MASK_DEVICE3 (0x0F) BIT0: IIN_REG_ACTIVE_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x0F, 1, 0)

	def write_iin_reg_active_mask(self, value):
		"""
		Write MASK_DEVICE3 (0x0F) BIT0: IIN_REG_ACTIVE_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x0F, 1, 0)	
	

	# ==================== MASK_FAULT0 (0x10) ====================

	def read_iin_ocp_mask(self):
		"""
		Read MASK_FAULT0 (0x10) BIT7: IIN_OCP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x10, 1, 7)

	def write_iin_ocp_mask(self, value):
		"""
		Write MASK_FAULT0 (0x10) BIT7: IIN_OCP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x10, 1, 7)

	def read_iin_ucp_fall_mask(self):
		"""
		Read MASK_FAULT0 (0x10) BIT6: IIN_UCP_FALL_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x10, 1, 6)

	def write_iin_ucp_fall_mask(self, value):
		"""
		Write MASK_FAULT0 (0x10) BIT6: IIN_UCP_FALL_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x10, 1, 6)

	def read_vin_in_ovp_mask(self):
		"""
		Read MASK_FAULT0 (0x10) BIT5: VIN_IN_OVP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x10, 1, 5)

	def write_vin_in_ovp_mask(self, value):
		"""
		Write MASK_FAULT0 (0x10) BIT5: VIN_IN_OVP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x10, 1, 5)

	def read_vb_out_ovp_mask(self):
		"""
		Read MASK_FAULT0 (0x10) BIT4: VB_OUT_OVP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x10, 1, 4)

	def write_vb_out_ovp_mask(self, value):
		"""
		Write MASK_FAULT0 (0x10) BIT4: VB_OUT_OVP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x10, 1, 4)

	def read_vout_ovp_mask(self):
		"""
		Read MASK_FAULT0 (0x10) BIT1: VOUT_OVP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x10, 1, 1)

	def write_vout_ovp_mask(self, value):
		"""
		Write MASK_FAULT0 (0x10) BIT1: VOUT_OVP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x10, 1, 1)

	def read_vbat_ovp_mask(self):
		"""
		Read MASK_FAULT0 (0x10) BIT0: VBAT_OVP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x10, 1, 0)

	def write_vbat_ovp_mask(self, value):
		"""
		Write MASK_FAULT0 (0x10) BIT0: VBAT_OVP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x10, 1, 0)


	# ==================== MASK_FAULT1 (0x11) ====================

	def read_pin_diag_fail_mask(self):
		"""
		Read MASK_FAULT1 (0x11) BIT7: PIN_DIAG_FAIL_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x11, 1, 7)

	def write_pin_diag_fail_mask(self, value):
		"""
		Write MASK_FAULT1 (0x11) BIT7: PIN_DIAG_FAIL_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x11, 1, 7)

	def read_cfly_open_mask(self):
		"""
		Read MASK_FAULT1 (0x11) BIT6: CFLY_OPEN_MASK
		Note: 0 = Not Masked | 1 = Masked (covers 0x06 bits[3:0])
		"""
		return self.bits_read(0x11, 1, 6)

	def write_cfly_open_mask(self, value):
		"""
		Write MASK_FAULT1 (0x11) BIT6: CFLY_OPEN_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x11, 1, 6)

	def read_cfly_short_mask(self):
		"""
		Read MASK_FAULT1 (0x11) BIT5: CFLY_SHORT_MASK
		Note: 0 = Not Masked | 1 = Masked (covers 0x06 bits[7:4])
		"""
		return self.bits_read(0x11, 1, 5)

	def write_cfly_short_mask(self, value):
		"""
		Write MASK_FAULT1 (0x11) BIT5: CFLY_SHORT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x11, 1, 5)

	def read_bst_fail_mask(self):
		"""
		Read MASK_FAULT1 (0x11) BIT4: BST_FAIL_MASK
		Note: 0 = Not Masked | 1 = Masked (covers 0x08 bits[7:0], 0x09 bits[6:7])
		"""
		return self.bits_read(0x11, 1, 4)

	def write_bst_fail_mask(self, value):
		"""
		Write MASK_FAULT1 (0x11) BIT4: BST_FAIL_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x11, 1, 4)



	def read_pmid_errorhi_mask(self):
		"""
		Read MASK_FAULT1 (0x11) BIT1: PMID_ERRORHI_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x11, 1, 1)

	def write_pmid_errorhi_mask(self, value):
		"""
		Write MASK_FAULT1 (0x11) BIT1: PMID_ERRORHI_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x11, 1, 1)

	def read_pmid_errorlo_mask(self):
		"""
		Read MASK_FAULT1 (0x11) BIT0: PMID_ERRORLO_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x11, 1, 0)

	def write_pmid_errorlo_mask(self, value):
		"""
		Write MASK_FAULT1 (0x11) BIT0: PMID_ERRORLO_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x11, 1, 0)


	# ==================== MASK_FAULT2 (0x12) ====================

	def read_ext_drv1_short_mask(self):
		"""
		Read MASK_FAULT2 (0x12) BIT3: EXT_DRV1_SHORT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x12, 1, 3)

	def write_ext_drv1_short_mask(self, value):
		"""
		Write MASK_FAULT2 (0x12) BIT3: EXT_DRV1_SHORT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x12, 1, 3)

	def read_ext_fet1_open_mask(self):
		"""
		Read MASK_FAULT2 (0x12) BIT2: EXT_FET1_OPEN_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x12, 1, 2)

	def write_ext_fet1_open_mask(self, value):
		"""
		Write MASK_FAULT2 (0x12) BIT2: EXT_FET1_OPEN_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x12, 1, 2)

	def read_ext_drv2_short_mask(self):
		"""
		Read MASK_FAULT2 (0x12) BIT1: EXT_DRV2_SHORT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x12, 1, 1)

	def write_ext_drv2_short_mask(self, value):
		"""
		Write MASK_FAULT2 (0x12) BIT1: EXT_DRV2_SHORT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x12, 1, 1)

	def read_ext_fet2_open_mask(self):
		"""
		Read MASK_FAULT2 (0x12) BIT0: EXT_FET2_OPEN_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x12, 1, 0)

	def write_ext_fet2_open_mask(self, value):
		"""
		Write MASK_FAULT2 (0x12) BIT0: EXT_FET2_OPEN_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x12, 1, 0)


	# ==================== MASK_FAULT3 (0x13) ====================

	def read_conv_ocp_mask(self):
		"""
		Read MASK_FAULT3 (0x13) BIT7: CONV_OCP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x13, 1, 7)

	def write_conv_ocp_mask(self, value):
		"""
		Write MASK_FAULT3 (0x13) BIT7: CONV_OCP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x13, 1, 7)

	def read_vo12out_uvp_mask(self):
		"""
		Read MASK_FAULT3 (0x13) BIT6: VO12OUT_UVP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x13, 1, 6)

	def write_vo12out_uvp_mask(self, value):
		"""
		Write MASK_FAULT3 (0x13) BIT6: VO12OUT_UVP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x13, 1, 6)

	def read_c1p2out_uvp_mask(self):
		"""
		Read MASK_FAULT3 (0x13) BIT5: C1P2OUT_UVP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x13, 1, 5)

	def write_c1p2out_uvp_mask(self, value):
		"""
		Write MASK_FAULT3 (0x13) BIT5: C1P2OUT_UVP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x13, 1, 5)

	def read_c1p2out_ovp_mask(self):
		"""
		Read MASK_FAULT3 (0x13) BIT4: C1P2OUT_OVP_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x13, 1, 4)

	def write_c1p2out_ovp_mask(self, value):
		"""
		Write MASK_FAULT3 (0x13) BIT4: C1P2OUT_OVP_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x13, 1, 4)

	def read_ntc_flt_mask(self):
		"""
		Read MASK_FAULT3 (0x13) BIT3: NTC_FLT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x13, 1, 3)

	def write_ntc_flt_mask(self, value):
		"""
		Write MASK_FAULT3 (0x13) BIT3: NTC_FLT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x13, 1, 3)

	def read_tshut_mask(self):
		"""
		Read MASK_FAULT3 (0x13) BIT2: TSHUT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x13, 1, 2)

	def write_tshut_mask(self, value):
		"""
		Write MASK_FAULT3 (0x13) BIT2: TSHUT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x13, 1, 2)

	def read_ss_fail_mask(self):
		"""
		Read MASK_FAULT3 (0x13) BIT1: SS_FAIL_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x13, 1, 1)

	def write_ss_fail_mask(self, value):
		"""
		Write MASK_FAULT3 (0x13) BIT1: SS_FAIL_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x13, 1, 1)

	def read_ss_timeout_mask(self):
		"""
		Read MASK_FAULT3 (0x13) BIT0: SS_TIMEOUT_MASK
		Note: 0 = Not Masked | 1 = Masked
		"""
		return self.bits_read(0x13, 1, 0)

	def write_ss_timeout_mask(self, value):
		"""
		Write MASK_FAULT3 (0x13) BIT0: SS_TIMEOUT_MASK
		Args: value: 0 = Not Masked | 1 = Masked
		"""
		self.bits_write(value, 0x13, 1, 0)



	# ==================== STAT_DEVICE0 (0x14) ====================

	def read_vb_out_present_stat(self):
		"""
		Read STAT_DEVICE0 (0x14) bit 7: VB_OUT_PRESENT_STAT
		Note: Status register - read only
		0: VB_OUT is lower than VB_OUT_PRESENT threshold | 1: VB_OUT is higher than VB_OUT_PRESENT threshold
		"""
		return self.bits_read(0x14, 1, 7)

	def read_cp_switching_stat(self):
		"""
		Read STAT_DEVICE0 (0x14) bit 6: CP_SWITCHING_STAT
		Note: Status register - read only
		0: CP is not switching | 1: CP is switching
		"""
		return self.bits_read(0x14, 1, 6)

	def read_vin_present_stat(self):
		"""
		Read STAT_DEVICE0 (0x14) bit 5: VIN_PRESENT_STAT
		Note: Status register - read only
		0: VIN is lower than VIN_PRESENT threshold | 1: VIN is higher than VIN_PRESENT threshold
		"""
		return self.bits_read(0x14, 1, 5)

	def read_vout_insert_stat(self):
		"""
		Read STAT_DEVICE0 (0x14) bit 4: VOUT_INSERT_STAT
		Note: Status register - read only
		0: VOUT is lower than VOUT_UVLO threshold | 1: VOUT is higher than VOUT_UVLO threshold
		"""
		return self.bits_read(0x14, 1, 4)

	def read_vout_th_rev_en_stat(self):
		"""
		Read STAT_DEVICE0 (0x14) bit 3: VOUT_TH_REV_EN_STAT
		Note: Status register - read only
		0: VOUT is lower than VOUT_TH_REV_EN threshold | 1: VOUT is higher than VOUT_TH_REV_EN threshold
		"""
		return self.bits_read(0x14, 1, 3)

	def read_vout_th_chg_en_stat(self):
		"""
		Read STAT_DEVICE0 (0x14) bit 2: VOUT_TH_CHG_EN_STAT
		Note: Status register - read only
		0: VOUT is lower than VOUT_TH_CHG_EN threshold | 1: VOUT is higher than VOUT_TH_CHG_EN threshold
		"""
		return self.bits_read(0x14, 1, 2)

	def read_vin_th_chg_en_stat(self):
		"""
		Read STAT_DEVICE0 (0x14) bit 1: VIN_TH_CHG_EN_STAT
		Note: Status register - read only
		0: VIN is lower than VIN_TH_CHG_EN threshold | 1: VIN is higher than VOUT_TH_CHG_EN threshold
		"""
		return self.bits_read(0x14, 1, 1)

	def read_vb_out_th_chg_en_stat(self):
		"""
		Read STAT_DEVICE0 (0x14) bit 0: VB_OUT_TH_CHG_EN_STAT
		Note: Status register - read only
		0: VIN is lower than VB_OUT_TH_CHG_EN threshold | 1: VIN is higher than VB_OUT_TH_CHG_EN threshold
		"""
		return self.bits_read(0x14, 1, 0)

	# ==================== STAT_DEVICE1 (0x15) ====================

	def read_vext_ovp_stat(self):
		"""
		Read STAT_DEVICE1 (0x15) bit 7: VEXT_OVP_STAT
		Note: Status register - read only
		0: VEXT is lower than VEXT_OVP threshold | 1: VEXT is higher than VEXT_OVP threshold
		"""
		return self.bits_read(0x15, 1, 7)

	def read_vext_drv_on_stat(self):
		"""
		Read STAT_DEVICE1 (0x15) bit 6: VEXT_DRV_ON_STAT
		Note: Status register - read only
		0: VEXT_DRV turns off | 1: VEXT_DRV turns on
		"""
		return self.bits_read(0x15, 1, 6)

	def read_vusb_insert_stat(self):
		"""
		Read STAT_DEVICE1 (0x15) bit 5: VUSB_INSERT_STAT
		Note: Status register - read only
		0: VUSB is lower than VUSB_UVLO threshold | 1: VUSB is higher than VUSB_UVLO threshold
		"""
		return self.bits_read(0x15, 1, 5)

	def read_vext_insert_stat(self):
		"""
		Read STAT_DEVICE1 (0x15) bit 4: VEXT_INSERT_STAT
		Note: Status register - read only
		0: VEXT_IN is lower than VEXT_IN_UVLO threshold | 1: VEXT_IN is higher than VEXT_IN_UVLO threshold
		"""
		return self.bits_read(0x15, 1, 4)

	def read_vusb_ovp_stat(self):
		"""
		Read STAT_DEVICE1 (0x15) bit 3: VUSB_OVP_STAT
		Note: Status register - read only
		0: VUSB is lower than VUSB_OVP threshold | 1: VUSB is higher than VUSB_OVP threshold
		"""
		return self.bits_read(0x15, 1, 3)

	def read_vusb_drv_on_stat(self):
		"""
		Read STAT_DEVICE1 (0x15) bit 2: VUSB_DRV_ON_STAT
		Note: Status register - read only
		0: VUSB_DRV turns off | 1: VUSB_DRV turns on
		"""
		return self.bits_read(0x15, 1, 2)

	def read_qb1_on_stat(self):
		"""
		Read STAT_DEVICE1 (0x15) bit 1: QB1_ON_STAT
		Note: Status register - read only
		0: QB1 turns off | 1: QB1 turns on
		"""
		return self.bits_read(0x15, 1, 1)

	def read_qb2_on_stat(self):
		"""
		Read STAT_DEVICE1 (0x15) bit 0: QB2_ON_STAT
		Note: Status register - read only
		0: QB2 turns off | 1: QB2 turns on
		"""
		return self.bits_read(0x15, 1, 0)

	# ==================== STAT_DEVICE2 (0x16) ====================

	def read_adc_done_stat(self):
		"""
		Read STAT_DEVICE2 (0x16) bit 7: ADC_DONE_STAT
		Note: Status register - read only
		0: ADC is not done | 1: ADC is done
		"""
		return self.bits_read(0x16, 1, 7)

	def read_wd_timeout_stat(self):
		"""
		Read STAT_DEVICE2 (0x16) bit 6: WD_TIMEOUT_ STAT
		Note: Status register - read only
		0: WD_TIMEOUT event does not happen | 1: WD_ TIMEOUT event happens
		"""
		return self.bits_read(0x16, 1, 6)

	def read_iin_ucp_rise_stat(self):
		"""
		Read STAT_DEVICE2 (0x16) bit 5: IIN_UCP_RISE_ STAT
		Note: Status register - read only
		0: IIN is less than IIN_UCP_RISE threshold | 1: IIN is higher than IIN_UCP_RISE threshold
		"""
		return self.bits_read(0x16, 1, 5)

	def read_vout_ok_sw_avdd_stat(self):
		"""
		Read STAT_DEVICE2 (0x16) bit 4: VOUT_OK_SW_AVDD_STAT
		Note: Status register - read only
		0: VOUT is lower than VOUT_SW_AVDD threshold | 1: VOUT is higher than VOUT_SW_AVDD threshold
		"""
		return self.bits_read(0x16, 1, 4)

	def read_tdie_reg_active_stat(self):
		"""
		Read STAT_DEVICE2 (0x16) bit 3: TDIE_REG_ACTIVE_ STAT
		Note: Status register - read only
		0: TDIE is lower than TDIE_REG threshold | 1: TDIE is higher than TDIE_REG threshold
		"""
		return self.bits_read(0x16, 1, 3)

	def read_vbat_reg_active_stat(self):
		"""
		Read STAT_DEVICE2 (0x16) bit 2: VBAT_REG_ACTIVE_ STAT
		Note: Status register - read only
		0: VBAT is lower than VBAT_REG threshold | 1: VBAT is higher than VBAT_REG threshold
		"""
		return self.bits_read(0x16, 1, 2)



	def read_iin_reg_active_stat(self):
		"""
		Read STAT_DEVICE2 (0x16) bit 0: IIN_REG_ACTIVE_ STAT
		Note: Status register - read only
		0: IIN is lower than IIN_REG threshold | 1: IIN is higher than IIN_REG threshold
		"""
		return self.bits_read(0x16, 1, 0)

	# ==================== STAT_FAULT0 (0x17) ====================

	def read_iin_ocp_stat(self):
		"""
		Read STAT_FAULT0 (0x17) bit 7: IIN_OCP_STAT
		Note: Status register - read only
		0: IIN is lower than IIN_OCP threshold | 1: IIN is higher than IIN_OCP threshold
		"""
		return self.bits_read(0x17, 1, 7)

	def read_iin_ucp_fall_stat(self):
		"""
		Read STAT_FAULT0 (0x17) bit 6: IIN_UCP_FALL_ STAT
		Note: Status register - read only
		0: IIN_UCP_FALLING threshold is not triggered | 1: IIN_UCP_FALLING threshold is triggered
		"""
		return self.bits_read(0x17, 1, 6)



	def read_vin_ovp_stat(self):
		"""
		Read STAT_FAULT0 (0x17) bit 3: VIN_OVP_ STAT
		Note: Status register - read only
		0: VIN is lower than VIN_OVP threshold | 1: VIN is higher than VIN_OVP threshold
		"""
		return self.bits_read(0x17, 1, 3)

	def read_vb_out_ovp_stat(self):
		"""
		Read STAT_FAULT0 (0x17) bit 2: VB_OUT_OVP_ STAT
		Note: Status register - read only
		0: VB_OUT is lower than VB_OUT threshold | 1: VB_OUT is higher than VB_OUT threshold
		"""
		return self.bits_read(0x17, 1, 2)

	def read_vout_ovp_stat(self):
		"""
		Read STAT_FAULT0 (0x17) bit 1: VOUT_OVP_STAT
		Note: Status register - read only
		0: VOUT is lower than VOUT_OVP threshold | 1: VOUT is higher than VOUT_OVP threshold
		"""
		return self.bits_read(0x17, 1, 1)

	def read_vbat_ovp_stat(self):
		"""
		Read STAT_FAULT0 (0x17) bit 0: VBAT_OVP_ STAT
		Note: Status register - read only
		0: VBAT is lower than VBAT_OVP threshold | 1: VBAT is higher than VBAT_OVP threshold
		"""
		return self.bits_read(0x17, 1, 0)

	# ==================== STAT_FAULT1 (0x18) ====================

	def read_c1a_short_stat(self):
		"""
		Read STAT_FAULT1 (0x18) bit 7: C1A_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: C1A SHORT
		"""
		return self.bits_read(0x18, 1, 7)

	def read_c1b_short_stat(self):
		"""
		Read STAT_FAULT1 (0x18) bit 6: C1B_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: C1B SHORT
		"""
		return self.bits_read(0x18, 1, 6)

	def read_c2a_short_stat(self):
		"""
		Read STAT_FAULT1 (0x18) bit 5: C2A_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: C2A SHORT
		"""
		return self.bits_read(0x18, 1, 5)

	def read_c2b_short_stat(self):
		"""
		Read STAT_FAULT1 (0x18) bit 4: C2B_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: C2B SHORT
		"""
		return self.bits_read(0x18, 1, 4)

	def read_c1a_open_stat(self):
		"""
		Read STAT_FAULT1 (0x18) bit 3: C1A_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: C1A OPEN
		"""
		return self.bits_read(0x18, 1, 3)

	def read_c1b_open_stat(self):
		"""
		Read STAT_FAULT1 (0x18) bit 2: C1B_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: C1B OPEN
		"""
		return self.bits_read(0x18, 1, 2)

	def read_c2a_open_stat(self):
		"""
		Read STAT_FAULT1 (0x18) bit 1: C2A_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: C2A OPEN
		"""
		return self.bits_read(0x18, 1, 1)

	def read_c2b_open_stat(self):
		"""
		Read STAT_FAULT1 (0x18) bit 0: C2B_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: C2B OPEN
		"""
		return self.bits_read(0x18, 1, 0)

	# ==================== STAT_FAULT2 (0x19) ====================

	def read_pin_diag_fail_stat(self):
		"""
		Read STAT_FAULT2 (0x19) bit 7: PIN_DIAG_FAIL_STAT
		Note: Status register - read only
		0: Normal | 1: PIN_DIAG_FAIL trigger
		"""
		return self.bits_read(0x19, 1, 7)



	def read_pmid_errorhi_stat(self):
		"""
		Read STAT_FAULT2 (0x19) bit 1: PMID_ERRORHI_STAT
		Note: Status register - read only
		0: Normal | 1: PMID_ERRORHI trigger
		"""
		return self.bits_read(0x19, 1, 1)

	def read_pmid_errorlo_stat(self):
		"""
		Read STAT_FAULT2 (0x19) bit 0: PMID_ERRORLO_STAT
		Note: Status register - read only
		0: Normal | 1: PMID_ERRORLO trigger
		"""
		return self.bits_read(0x19, 1, 0)

	# ==================== STAT_FAULT3 (0x1A) ====================

	def read_bst1a_short_stat(self):
		"""
		Read STAT_FAULT3 (0x1A) bit 7: BST1A_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: BST1A SHORT
		"""
		return self.bits_read(0x1A, 1, 7)

	def read_bst1b_short_stat(self):
		"""
		Read STAT_FAULT3 (0x1A) bit 6: BST1B_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: BST1B SHORT
		"""
		return self.bits_read(0x1A, 1, 6)

	def read_bst2_short_stat(self):
		"""
		Read STAT_FAULT3 (0x1A) bit 5: BST2_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: BST2 SHORT
		"""
		return self.bits_read(0x1A, 1, 5)

	def read_bst3a_short_stat(self):
		"""
		Read STAT_FAULT3 (0x1A) bit 4: BST3A_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: BST3A SHORT
		"""
		return self.bits_read(0x1A, 1, 4)

	def read_bst3b_short_stat(self):
		"""
		Read STAT_FAULT3 (0x1A) bit 3: BST3B_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: BST3B SHORT
		"""
		return self.bits_read(0x1A, 1, 3)

	def read_bst1a_open_stat(self):
		"""
		Read STAT_FAULT3 (0x1A) bit 2: BST1A_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: BST1A OPEN
		"""
		return self.bits_read(0x1A, 1, 2)

	def read_bst1b_open_stat(self):
		"""
		Read STAT_FAULT3 (0x1A) bit 1: BST1B_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: BST1B OPEN
		"""
		return self.bits_read(0x1A, 1, 1)

	def read_bst2_open_stat(self):
		"""
		Read STAT_FAULT3 (0x1A) bit 0: BST2_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: BST2 OPEN
		"""
		return self.bits_read(0x1A, 1, 0)

	# ==================== STAT_FAULT4 (0x1B) ====================

	def read_bst3a_open_stat(self):
		"""
		Read STAT_FAULT4 (0x1B) bit 7: BST3A_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: BST3A OPEN
		"""
		return self.bits_read(0x1B, 1, 7)

	def read_bst3b_open_stat(self):
		"""
		Read STAT_FAULT4 (0x1B) bit 6: BST3B_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: BST3B OPEN
		"""
		return self.bits_read(0x1B, 1, 6)


	def read_ext1_drv_short_stat(self):
		"""
		Read STAT_FAULT4 (0x1B) bit 3: EXT1_DRV_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: EXT1_DRV_SHORT trigger
		"""
		return self.bits_read(0x1B, 1, 3)

	def read_ext1_fet_open_stat(self):
		"""
		Read STAT_FAULT4 (0x1B) bit 2: EXT1_FET_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: EXT1_FET_OPEN trigger
		"""
		return self.bits_read(0x1B, 1, 2)

	def read_ext2_drv_short_stat(self):
		"""
		Read STAT_FAULT4 (0x1B) bit 1: EXT2_DRV_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: EXT2_DRV_SHORT trigger
		"""
		return self.bits_read(0x1B, 1, 1)

	def read_ext2_fet_open_stat(self):
		"""
		Read STAT_FAULT4 (0x1B) bit 0: EXT2_FET_OPEN_STAT
		Note: Status register - read only
		0: Normal | 1: EXT2_FET_OPEN trigger
		"""
		return self.bits_read(0x1B, 1, 0)

	# ==================== STAT_FAULT5 (0x1C) ====================

	def read_c1a_short_ph3_stat(self):
		"""
		Read STAT_FAULT5 (0x1C) bit 7: C1A_SHORT_PH3_STAT
		Note: Status register - read only
		0: Normal | 1: C1A SHORT in PH3
		"""
		return self.bits_read(0x1C, 1, 7)

	def read_c1b_short_ph3_stat(self):
		"""
		Read STAT_FAULT5 (0x1C) bit 6: C1B_SHORT_PH3_STAT
		Note: Status register - read only
		0: Normal | 1: C1B SHORT in PH3
		"""
		return self.bits_read(0x1C, 1, 6)

	def read_c2a_short_ph3_stat(self):
		"""
		Read STAT_FAULT5 (0x1C) bit 5: C2A_SHORT_PH3_STAT
		Note: Status register - read only
		0: Normal | 1: C2A SHORT in PH3
		"""
		return self.bits_read(0x1C, 1, 5)

	def read_c2b_short_ph3_stat(self):
		"""
		Read STAT_FAULT5 (0x1C) bit 4: C2B_SHORT_PH3_STAT
		Note: Status register - read only
		0: Normal | 1: C2B SHORT in PH3
		"""
		return self.bits_read(0x1C, 1, 4)

	def read_q5_short_stat(self):
		"""
		Read STAT_FAULT5 (0x1C) bit 3: Q5_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: Q5 SHORT
		"""
		return self.bits_read(0x1C, 1, 3)

	def read_c1pa_c1pb_short_stat(self):
		"""
		Read STAT_FAULT5 (0x1C) bit 2: C1PA_C1PB_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: C1PA_C1PB SHORT
		"""
		return self.bits_read(0x1C, 1, 2)

	def read_q3a_short_stat(self):
		"""
		Read STAT_FAULT5 (0x1C) bit 1: Q3A_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: Q3A SHORT
		"""
		return self.bits_read(0x1C, 1, 1)

	def read_q3b_short_stat(self):
		"""
		Read STAT_FAULT5 (0x1C) bit 0: Q3B_SHORT_STAT
		Note: Status register - read only
		0: Normal | 1: Q3B_SHORT
		"""
		return self.bits_read(0x1C, 1, 0)

	# ==================== STAT_FAULT6 (0x1D) ====================

	def read_conv_ocp_stat(self):
		"""
		Read STAT_FAULT6 (0x1D) bit 7: CONV_OCP_STAT
		Note: Status register - read only
		0: CONV_OCP is not triggered | 1: CONV_OCP is triggered
		"""
		return self.bits_read(0x1D, 1, 7)

	def read_vo12out_uvp_stat(self):
		"""
		Read STAT_FAULT6 (0x1D) bit 6: VO12OUT_UVP_STAT
		Note: Status register - read only
		0: VO12OUT_UVP is not triggered | 1: VO12OUT_UVP is triggered
		"""
		return self.bits_read(0x1D, 1, 6)

	def read_c1p2out_uvp_stat(self):
		"""
		Read STAT_FAULT6 (0x1D) bit 5: C1P2OUT_UVP_ STAT
		Note: Status register - read only
		0: C1P2OUT_UVP is not triggered | 1: C1P2OUT_UVP is triggered
		"""
		return self.bits_read(0x1D, 1, 5)

	def read_c1p2out_ovp_stat(self):
		"""
		Read STAT_FAULT6 (0x1D) bit 4: C1P2OUT_OVP_ STAT
		Note: Status register - read only
		0: C1P2OUT_OVP is not triggered | 1: C1P2OUT_OVP is triggered
		"""
		return self.bits_read(0x1D, 1, 4)

	def read_ntc_flt_stat(self):
		"""
		Read STAT_FAULT6 (0x1D) bit 3: NTC_FLT_ STAT
		Note: Status register - read only
		0: NTC_FLT is not triggered | 1: NTC_FLT is triggered
		"""
		return self.bits_read(0x1D, 1, 3)

	def read_tshut_stat(self):
		"""
		Read STAT_FAULT6 (0x1D) bit 2: TSHUT_ STAT
		Note: Status register - read only
		0: TSHUT is not triggered | 1: TSHUT is triggered
		"""
		return self.bits_read(0x1D, 1, 2)

	def read_ss_fail_stat(self):
		"""
		Read STAT_FAULT6 (0x1D) bit 1: SS_FAIL_ STAT
		Note: Status register - read only
		0: SS_FAIL event does not happen | 1: SS_FAIL event happens
		"""
		return self.bits_read(0x1D, 1, 1)

	def read_ss_timeout_stat(self):
		"""
		Read STAT_FAULT6 (0x1D) bit 0: SS_TIMEOUT_ STAT
		Note: Status register - read only
		0: SS_TIMEOUT event does not happen | 1: SS_ TIMEOUT event happens
		"""
		return self.bits_read(0x1D, 1, 0)


	# ==================== CTRL0 (0x1E) ====================

	def read_cp_en(self):
		"""
		Read CTRL0 (0x1E) bit 7: CP_EN
		Note: RW
		0 = Charge pump disabled (default) | 1 = Charge pump enabled
		"""
		return self.bits_read(0x1E, 1, 7)

	def write_cp_en(self, value):
		"""
		Write CTRL0 (0x1E) bit 7: CP_EN
		0 = Charge pump disabled (default) | 1 = Charge pump enabled
		"""
		self.bits_write(value, 0x1E, 1, 7)

	def read_qb1_ctrl2(self):
		"""
		Read CTRL0 (0x1E) bit 6: QB1_CTRL2
		Note: RW
		0: off (Default) | 1: If MODE=b0xx (Forward mode), QB1 will turn on after CP_EN=1, then this bit will be locked, until CP_EN=0; if MODE=b1xx (Reverse mode), QB1 will turn on after soft-start is done
		"""
		return self.bits_read(0x1E, 1, 6)

	def write_qb1_ctrl2(self, value):
		"""
		Write CTRL0 (0x1E) bit 6: QB1_CTRL2
		0: off (Default) | 1: If MODE=b0xx (Forward mode), QB1 will turn on after CP_EN=1, then this bit will be locked, until CP_EN=0; if MODE=b1xx (Reverse mode), QB1 will turn on after soft-start is done
		"""
		self.bits_write(value, 0x1E, 1, 6)

	def read_qb2_ctrl1(self):
		"""
		Read CTRL0 (0x1E) bit 5: QB2_CTRL1
		Note: RW
		0: Manual (Default when VB_EN=LOW/Floating) | 1: Auto (Default when VB_EN=HIGH)
		"""
		return self.bits_read(0x1E, 1, 5)

	def write_qb2_ctrl1(self, value):
		"""
		Write CTRL0 (0x1E) bit 5: QB2_CTRL1
		0: Manual (Default when VB_EN=LOW/Floating) | 1: Auto (Default when VB_EN=HIGH)
		"""
		self.bits_write(value, 0x1E, 1, 5)

	def read_qb2_ctrl2(self):
		"""
		Read CTRL0 (0x1E) bit 4: QB2_CTRL2
		Note: RW
		Only valid when QB2_CTRL1 =0 (manual mode) | 0: off (Default) | 1: If MODE=b0xx (Forward mode), QB2 need to turn on before CP_EN=1, then this bit will be locked, until CP_EN=0; if MODE=b1xx (Reverse mode), QB2 will turn on after soft-start is done. | This bit has no effect when QB1_CTRL = 1 (cannot set to 1)
		"""
		return self.bits_read(0x1E, 1, 4)

	def write_qb2_ctrl2(self, value):
		"""
		Write CTRL0 (0x1E) bit 4: QB2_CTRL2
		Only valid when QB2_CTRL1 =0 (manual mode) | 0: off (Default) | 1: If MODE=b0xx (Forward mode), QB2 need to turn on before CP_EN=1, then this bit will be locked, until CP_EN=0; if MODE=b1xx (Reverse mode), QB2 will turn on after soft-start is done. | This bit has no effect when QB1_CTRL = 1 (cannot set to 1)
		"""
		self.bits_write(value, 0x1E, 1, 4)

	def read_mode(self):
		"""
		Read CTRL0 (0x1E) bit 3:0: MODE
		Note: RW
		These bits decide the operation mode | 000 = Forward 4:1 charger mode (default) | 001 = Forward 3:1 charger mode | 010 = Forward 2:1 charger mode | 011 = Forward 1:1 charger mode | 100 = Reverse 1:4 converter mode | 101 = Reverse 1:3 converter mode | 110 = Reverse 1:2 converter mode | 111 = Reverse 1:1 converter mode | 1xxx = VDC mode | These bits cannot be changed when CP_EN=1
		"""
		return self.bits_read(0x1E, 4, 0)

	def write_mode(self, value):
		"""
		Write CTRL0 (0x1E) bit 3:0: MODE
		These bits decide the operation mode | 000 = Forward 4:1 charger mode (default) | 001 = Forward 3:1 charger mode | 010 = Forward 2:1 charger mode | 011 = Forward 1:1 charger mode | 100 = Reverse 1:4 converter mode | 101 = Reverse 1:3 converter mode | 110 = Reverse 1:2 converter mode | 111 = Reverse 1:1 converter mode | 1xxx = VDC mode | These bits cannot be changed when CP_EN=1
		"""
		self.bits_write(value, 0x1E, 4, 0)


    # ==================== CTRL1 (0x1F) ====================

	def read_vin_present_dis(self):
		"""
		Read CTRL1 (0x1F) bit 7: VIN_PRESENT_DIS
		Note: RW
		0: Enable the VIN_PRESENT precondition (default) | 1: Disable the VIN_PRESENT precondition
		"""
		return self.bits_read(0x1F, 1, 7)

	def write_vin_present_dis(self, value):
		"""
		Write CTRL1 (0x1F) bit 7: VIN_PRESENT_DIS
		0: Enable the VIN_PRESENT precondition (default) | 1: Disable the VIN_PRESENT precondition
		"""
		self.bits_write(value, 0x1F, 1, 7)

	def read_vb_out_present_dis(self):
		"""
		Read CTRL1 (0x1F) bit 6: VB_OUT_PRESENT_DIS
		Note: RW
		0: Enable the VB_OUT_PRESENT precondition (default) | 1: Disable the VB_OUT_PRESENT precondition
		"""
		return self.bits_read(0x1F, 1, 6)

	def write_vb_out_present_dis(self, value):
		"""
		Write CTRL1 (0x1F) bit 6: VB_OUT_PRESENT_DIS
		0: Enable the VB_OUT_PRESENT precondition (default) | 1: Disable the VB_OUT_PRESENT precondition
		"""
		self.bits_write(value, 0x1F, 1, 6)

	def read_ss_timeout(self):
		"""
		Read CTRL1 (0x1F) bit 5:4: SS_TIMEOUT
		Note: RW
		Adjustable timeout for IIN to rise to the IIN_UCP_RISE_THRESHOLD | 00: SS Timeout Disabled | 01: 320ms | 10: 1.28s | 11: 10.24s (default)
		"""
		return self.bits_read(0x1F, 2, 4)

	def write_ss_timeout(self, value):
		"""
		Write CTRL1 (0x1F) bit 5:4: SS_TIMEOUT
		Adjustable timeout for IIN to rise to the IIN_UCP_RISE_THRESHOLD | 00: SS Timeout Disabled | 01: 320ms | 10: 1.28s | 11: 10.24s (default)
		"""
		self.bits_write(value, 0x1F, 2, 4)

	def read_ss_fail_dis(self):
		"""
		Read CTRL1 (0x1F) bit 3: SS_FAIL_DIS
		Note: RW
		0: Enable the SS_FAIL protection (default) | 1: Disable the SS_FAIL protection
		"""
		return self.bits_read(0x1F, 1, 3)

	def write_ss_fail_dis(self, value):
		"""
		Write CTRL1 (0x1F) bit 3: SS_FAIL_DIS
		0: Enable the SS_FAIL protection (default) | 1: Disable the SS_FAIL protection
		"""
		self.bits_write(value, 0x1F, 1, 3)

	def read_iin_ucp_fall_blanking_set(self):
		"""
		Read CTRL1 (0x1F) bit 2:1: IIN_UCP_FALL_BLANKING_SET
		Note: RW
		These two bits decide the blanking time of IIN_UCP_FALL protection after the device start switching | 00: 100ms (default) | 01: 200ms | 10: 400ms | 11: 800ms
		"""
		return self.bits_read(0x1F, 2, 1)

	def write_iin_ucp_fall_blanking_set(self, value):
		"""
		Write CTRL1 (0x1F) bit 2:1: IIN_UCP_FALL_BLANKING_SET
		These two bits decide the blanking time of IIN_UCP_FALL protection after the device start switching | 00: 100ms (default) | 01: 200ms | 10: 400ms | 11: 800ms
		"""
		self.bits_write(value, 0x1F, 2, 1)

	def read_iin_ucp_en_method_sel(self):
		"""
		Read CTRL1 (0x1F) bit 0: IIN_UCP_EN_METHOD_SEL
		Note: RW
		This bit determines when IIN_UCP_FALL protection will be enabled | 0: The IIN_UCP_FALL protection will be enabled once IIN rising about IIN_UCP rising threshold (default) | 1: The IIN_UCP_FALL protection will be enabled after the IIN_UCP_FALL blanking time
		"""
		return self.bits_read(0x1F, 1, 0)

	def write_iin_ucp_en_method_sel(self, value):
		"""
		Write CTRL1 (0x1F) bit 0: IIN_UCP_EN_METHOD_SEL
		This bit determines when IIN_UCP_FALL protection will be enabled | 0: The IIN_UCP_FALL protection will be enabled once IIN rising about IIN_UCP rising threshold (default) | 1: The IIN_UCP_FALL protection will be enabled after the IIN_UCP_FALL blanking time
		"""
		self.bits_write(value, 0x1F, 1, 0)


	# ==================== CTRL2 (0x20) ====================

	def read_vusb_ovp_sel(self):
		"""
		Read CTRL2 (0x20) bit 7: VUSB_OVP_SEL
		Note: RW
		0: VUSB_OVP trigger only turn off EXT FET (default) | 1: VUSB_OVP trigger will turn off EXT FET, QB and switching
		"""
		return self.bits_read(0x20, 1, 7)

	def write_vusb_ovp_sel(self, value):
		"""
		Write CTRL2 (0x20) bit 7: VUSB_OVP_SEL
		0: VUSB_OVP trigger only turn off EXT FET (default) | 1: VUSB_OVP trigger will turn off EXT FET, QB and switching
		"""
		self.bits_write(value, 0x20, 1, 7)

	def read_vext_ovp_sel(self):
		"""
		Read CTRL2 (0x20) bit 6: VEXT_OVP_SEL
		Note: RW
		0: VEXT_OVP trigger only turn off EXT FET (default) | 1: VEXT_OVP trigger will turn off EXT FET, QB and switching
		"""
		return self.bits_read(0x20, 1, 6)

	def write_vext_ovp_sel(self, value):
		"""
		Write CTRL2 (0x20) bit 6: VEXT_OVP_SEL
		0: VEXT_OVP trigger only turn off EXT FET (default) | 1: VEXT_OVP trigger will turn off EXT FET, QB and switching
		"""
		self.bits_write(value, 0x20, 1, 6)

	def read_freq_shift(self):
		"""
		Read CTRL2 (0x20) bit 5:4: FREQ_SHIFT
		Note: RW
		Adjust FSW for EMI | 00 = Nominal frequency (default) | 01 = -10% | 10 = +10% | 11 = Spread spectrum varies frequency +-10%
		"""
		return self.bits_read(0x20, 2, 4)

	def write_freq_shift(self, value):
		"""
		Write CTRL2 (0x20) bit 5:4: FREQ_SHIFT
		Adjust FSW for EMI | 00 = Nominal frequency (default) | 01 = -10% | 10 = +10% | 11 = Spread spectrum varies frequency +-10%
		"""
		self.bits_write(value, 0x20, 2, 4)

	def read_fsw_set(self):
		"""
		Read CTRL2 (0x20) bit 3:0: FSW_SET
		Note: RW
		Set the CP switching frequency | Offset: 400kHz | Step: 100kHz | Range: 400kHz (b0000) - 1900kHz (b1111) | Default: 1200kHz (b1000) | <100:gain> | <400:offset>
		"""
		return self.bits_read(0x20, 4, 0)

	def write_fsw_set(self, value):
		"""
		Write CTRL2 (0x20) bit 3:0: FSW_SET
		Set the CP switching frequency | Offset: 400kHz | Step: 100kHz | Range: 400kHz (b0000) - 1900kHz (b1111) | Default: 1200kHz (b1000) | <100:gain> | <400:offset>
		"""
		self.bits_write(value, 0x20, 4, 0)


	# ==================== CTRL3 (0x21) ====================

	def read_sync_en(self):
		"""
		Read CTRL3 (0x21) bit 7: SYNC_EN
		Note: RW
		0: Disable (Default)  | 1: Enable
		"""
		return self.bits_read(0x21, 1, 7)

	def write_sync_en(self, value):
		"""
		Write CTRL3 (0x21) bit 7: SYNC_EN
		0: Disable (Default)  | 1: Enable
		"""
		self.bits_write(value, 0x21, 1, 7)

	def read_sync_role(self):
		"""
		Read CTRL3 (0x21) bit 6: SYNC_ROLE
		Note: RW
		This bit is valid when SYNC_EN=0 | 0: Sub (Default)  | 1: Main
		"""
		return self.bits_read(0x21, 1, 6)

	def write_sync_role(self, value):
		"""
		Write CTRL3 (0x21) bit 6: SYNC_ROLE
		This bit is valid when SYNC_EN=0 | 0: Sub (Default)  | 1: Main
		"""
		self.bits_write(value, 0x21, 1, 6)

	def read_sync_out(self):
		"""
		Read CTRL3 (0x21) bit 5:4: SYNC_OUT
		Note: RW
		00: Hi-Z (default) | 01: Output Low | 10: Output High | 11: Hi-Z
		"""
		return self.bits_read(0x21, 2, 4)

	def write_sync_out(self, value):
		"""
		Write CTRL3 (0x21) bit 5:4: SYNC_OUT
		00: Hi-Z (default) | 01: Output Low | 10: Output High | 11: Hi-Z
		"""
		self.bits_write(value, 0x21, 2, 4)

	def read_dual_config(self):
		"""
		Read CTRL3 (0x21) bit 3: DUAL_CONFIG
		Note: RW
		This bit is valid when SYNC_EN=0 | 0: Default | 1: ADC SYNC
		"""
		return self.bits_read(0x21, 1, 3)

	def write_dual_config(self, value):
		"""
		Write CTRL3 (0x21) bit 3: DUAL_CONFIG
		This bit is valid when SYNC_EN=0 | 0: Default | 1: ADC SYNC
		"""
		self.bits_write(value, 0x21, 1, 3)



	def read_pmid_in_range_dis(self):
		"""
		Read CTRL3 (0x21) bit 1: PMID_IN_RANGE_DIS
		Note: RW
		0: Enable the PMID_IN_RANGE protection (default) | 1: Disable the PMID_IN_RANGE protection
		"""
		return self.bits_read(0x21, 1, 1)

	def write_pmid_in_range_dis(self, value):
		"""
		Write CTRL3 (0x21) bit 1: PMID_IN_RANGE_DIS
		0: Enable the PMID_IN_RANGE protection (default) | 1: Disable the PMID_IN_RANGE protection
		"""
		self.bits_write(value, 0x21, 1, 1)

	def read_pmid_pd_en(self):
		"""
		Read CTRL3 (0x21) bit 0: PMID_PD_EN
		Note: RW
		0 = PMID pull-down disabled (default) | 1 = PMID pull-down enabled
		"""
		return self.bits_read(0x21, 1, 0)

	def write_pmid_pd_en(self, value):
		"""
		Write CTRL3 (0x21) bit 0: PMID_PD_EN
		0 = PMID pull-down disabled (default) | 1 = PMID pull-down enabled
		"""
		self.bits_write(value, 0x21, 1, 0)


	# ==================== CTRL4 (0x22) ====================

	def read_reg_rst(self):
		"""
		Read CTRL4 (0x22) bit 7: REG_RST
		Note: RW
		0 = No register reset (default) | 1 = Reset registers to their default values
		"""
		return self.bits_read(0x22, 1, 7)

	def write_reg_rst(self, value):
		"""
		Write CTRL4 (0x22) bit 7: REG_RST
		0 = No register reset (default) | 1 = Reset registers to their default values
		"""
		self.bits_write(value, 0x22, 1, 7)

	def read_vusb_shutdown_set(self):
		"""
		Read CTRL4 (0x22) bit 6: VUSB_SHUTDOWN_SET
		Note: RW
		0 = No effect | 1 = IC will enter into VUSB_SHUTDOWN mode, only I2C function is available in this mode. This bit should be cleared before enter Standby mode
		"""
		return self.bits_read(0x22, 1, 6)

	def write_vusb_shutdown_set(self, value):
		"""
		Write CTRL4 (0x22) bit 6: VUSB_SHUTDOWN_SET
		0 = No effect | 1 = IC will enter into VUSB_SHUTDOWN mode, only I2C function is available in this mode. This bit should be cleared before enter Standby mode
		"""
		self.bits_write(value, 0x22, 1, 6)

	def read_standby_mode_set(self):
		"""
		Read CTRL4 (0x22) bit 5: STANDBY_MODE_SET
		Note: RW
		Only valid in shutdown mode and standby mode. | 0: Shutdown mode (Default) | 1: Standby mode.
		"""
		return self.bits_read(0x22, 1, 5)

	def write_standby_mode_set(self, value):
		"""
		Write CTRL4 (0x22) bit 5: STANDBY_MODE_SET
		Only valid in shutdown mode and standby mode. | 0: Shutdown mode (Default) | 1: Standby mode.
		"""
		self.bits_write(value, 0x22, 1, 5)

	def read_wd_vusb_shutdown_en(self):
		"""
		Read CTRL4 (0x22) bit 4: WD_VUSB_SHUTDOWN_EN
		Note: RW
		0: Disable | 1: Enable. If this is set to 1, VUSB_SHUTDOWN_SET becomes 0 when watchdog timer is expired. This bit is set to 0 when shutdown mode are set.
		"""
		return self.bits_read(0x22, 1, 4)

	def write_wd_vusb_shutdown_en(self, value):
		"""
		Write CTRL4 (0x22) bit 4: WD_VUSB_SHUTDOWN_EN
		0: Disable | 1: Enable. If this is set to 1, VUSB_SHUTDOWN_SET becomes 0 when watchdog timer is expired. This bit is set to 0 when shutdown mode are set.
		"""
		self.bits_write(value, 0x22, 1, 4)

	def read_wd_standby_en(self):
		"""
		Read CTRL4 (0x22) bit 3: WD_STANDBY _EN
		Note: RW
		0: Disable | 1: Enable. If this is set to 1, shutdown mode is forced and STANDBY_MODE_SET becomes 0 when watchdog timer is expired. This bit is set to 0 when shutdown mode or active mode are set.
		"""
		return self.bits_read(0x22, 1, 3)

	def write_wd_standby_en(self, value):
		"""
		Write CTRL4 (0x22) bit 3: WD_STANDBY _EN
		0: Disable | 1: Enable. If this is set to 1, shutdown mode is forced and STANDBY_MODE_SET becomes 0 when watchdog timer is expired. This bit is set to 0 when shutdown mode or active mode are set.
		"""
		self.bits_write(value, 0x22, 1, 3)

	def read_wd_timeout_dis(self):
		"""
		Read CTRL4 (0x22) bit 2: WD_TIMEOUT_DIS
		Note: RW
		0 = Enable watchdog | 1 = Disable watchdog (default)
		"""
		return self.bits_read(0x22, 1, 2)

	def write_wd_timeout_dis(self, value):
		"""
		Write CTRL4 (0x22) bit 2: WD_TIMEOUT_DIS
		0 = Enable watchdog | 1 = Disable watchdog (default)
		"""
		self.bits_write(value, 0x22, 1, 2)

	def read_wd_timeout(self):
		"""
		Read CTRL4 (0x22) bit 1:0: WD_TIMEOUT
		Note: RW
		Watchdog Timeout protection | 00: 4s (default) | 01: 8s | 10: 16s | 11: 32s
		"""
		return self.bits_read(0x22, 2, 0)

	def write_wd_timeout(self, value):
		"""
		Write CTRL4 (0x22) bit 1:0: WD_TIMEOUT
		Watchdog Timeout protection | 00: 4s (default) | 01: 8s | 10: 16s | 11: 32s
		"""
		self.bits_write(value, 0x22, 2, 0)

	def read_vusb_sw_ctrl1(self):
		"""
		Read VUSB_CTRL (0x23) bit 7: VUSB_SW_CTRL1
		Note: RW
		0: Manual (Default when VB_EN=Low) | 1: Auto (Default when VB_EN=Floating or High)
		"""
		return self.bits_read(0x23, 1, 7)

	def write_vusb_sw_ctrl1(self, value):
		"""
		Write VUSB_CTRL (0x23) bit 7: VUSB_SW_CTRL1
		0: Manual (Default when VB_EN=Low) | 1: Auto (Default when VB_EN=Floating or High)
		"""
		self.bits_write(value, 0x23, 1, 7)

	def read_vusb_sw_ctrl2(self):
		"""
		Read VUSB_CTRL (0x23) bit 6: VUSB_SW_CTRL2
		Note: RW (only valid when VUSB_SW_CTRL1=0)
		0: OFF (default) | 1: ON (bit auto-cleared when VUSB invalid)
		"""
		return self.bits_read(0x23, 1, 6)

	def write_vusb_sw_ctrl2(self, value):
		"""
		Write VUSB_CTRL (0x23) bit 6: VUSB_SW_CTRL2
		0: OFF (default) | 1: ON (bit auto-cleared when VUSB invalid)
		"""
		self.bits_write(value, 0x23, 1, 6)

	def read_vusb_off_gate_ctrl(self):
		"""
		Read VUSB_CTRL (0x23) bit 5: VUSB_OFF_GATE_CTRL
		Note: RW
		0: VUSB_DRV pull down to GND when FET OFF (Default when VB_EN=Floating/HIGH) | 1: VUSB_DRV floating when FET OFF (Default when VB_EN=LOW)
		"""
		return self.bits_read(0x23, 1, 5)

	def write_vusb_off_gate_ctrl(self, value):
		"""
		Write VUSB_CTRL (0x23) bit 5: VUSB_OFF_GATE_CTRL
		0: VUSB_DRV pull down to GND | 1: VUSB_DRV floating
		"""
		self.bits_write(value, 0x23, 1, 5)

	def read_vusb_ovp_dis(self):
		"""
		Read VUSB_CTRL (0x23) bit 4: VUSB_OVP_DIS
		Note: RW
		0: Enable VUSB_OVP (default) | 1: Disable VUSB_OVP
		"""
		return self.bits_read(0x23, 1, 4)

	def write_vusb_ovp_dis(self, value):
		"""
		Write VUSB_CTRL (0x23) bit 4: VUSB_OVP_DIS
		0: Enable VUSB_OVP (default) | 1: Disable VUSB_OVP
		"""
		self.bits_write(value, 0x23, 1, 4)

	def write_vusb_ovp(self, voltage):
		"""
		Write VUSB_CTRL (0x23) bit 3:0: VUSB_OVP
		Args: voltage — actual voltage in V (7.5V or 11V ~ 25V, step 1V)
		Raises: ValueError if voltage out of range
		"""
		if voltage == 7.5:
			reg_val = 0xF
		elif 11.0 <= voltage <= 25.0:
			reg_val = int(voltage - 11)
		else:
			raise ValueError(f"VUSB_OVP voltage {voltage}V out of range! Valid: 7.5V or 11V~25V (step 1V)")
		self.bits_write(reg_val, 0x23, 4, 0)

	def read_vusb_ovp(self):
		"""
		Read VUSB_CTRL (0x23) bit 3:0: VUSB_OVP
		Returns: actual voltage in V (0xF → 7.5V, others → 11V + reg_val × 1V)
		"""
		reg_val = self.bits_read(0x23, 4, 0)
		if reg_val == 0xF:
			return 7.5
		return 11.0 + reg_val



	def read_vext_sw_ctrl1(self):
		"""
		Read VEXT_CTRL (0x24) bit 7: VEXT_SW_CTRL1
		0: Manual (Default when VB_EN=Low/High) | 1: Auto (Default when VB_EN=Floating)
		"""
		return self.bits_read(0x24, 1, 7)

	def write_vext_sw_ctrl1(self, value):
		"""
		Write VEXT_CTRL (0x24) bit 7: VEXT_SW_CTRL1
		0: Manual (Default when VB_EN=Low/High) | 1: Auto (Default when VB_EN=Floating)
		"""
		self.bits_write(value, 0x24, 1, 7)

	def read_vext_sw_ctrl2(self):
		"""
		Read VEXT_CTRL (0x24) bit 6: VEXT_SW_CTRL2
		Note: RW (only valid when VEXT_SW_CTRL1=0)
		0: OFF (default) | 1: ON (bit auto-cleared when VEXT is not valid)
		"""
		return self.bits_read(0x24, 1, 6)

	def write_vext_sw_ctrl2(self, value):
		"""
		Write VEXT_CTRL (0x24) bit 6: VEXT_SW_CTRL2
		0: OFF (default) | 1: ON (bit auto-cleared when VEXT is not valid)
		"""
		self.bits_write(value, 0x24, 1, 6)

	def read_vext_off_gate_ctrl(self):
		"""
		Read VEXT_CTRL (0x24) bit 5: VEXT_OFF_GATE_CTRL
		Note: RW
		0: VEXT_DRV pull down to GND when FET OFF (default) | 1: VEXT_DRV floating when FET OFF
		"""
		return self.bits_read(0x24, 1, 5)

	def write_vext_off_gate_ctrl(self, value):
		"""
		Write VEXT_CTRL (0x24) bit 5: VEXT_OFF_GATE_CTRL
		0: VEXT_DRV pull down to GND | 1: VEXT_DRV floating
		"""
		self.bits_write(value, 0x24, 1, 5)

	def read_vext_ovp_dis(self):
		"""
		Read VEXT_CTRL (0x24) bit 4: VEXT_OVP_DIS
		Note: RW
		0: Enable VEXT_OVP (default) | 1: Disable VEXT_OVP
		"""
		return self.bits_read(0x24, 1, 4)

	def write_vext_ovp_dis(self, value):
		"""
		Write VEXT_CTRL (0x24) bit 4: VEXT_OVP_DIS
		0: Enable VEXT_OVP (default) | 1: Disable VEXT_OVP
		"""
		self.bits_write(value, 0x24, 1, 4)

	def write_vext_ovp(self, voltage):
		"""
		Write VEXT_CTRL (0x24) bit 3:0: VEXT_OVP
		Args: voltage — actual voltage in V (7.5V or 11V ~ 25V, step 1V)
		Raises: ValueError if voltage out of range
		"""
		if voltage == 7.5:
			reg_val = 0xF
		elif 11.0 <= voltage <= 25.0:
			reg_val = int(voltage - 11)
		else:
			raise ValueError(f"VEXT_OVP voltage {voltage}V out of range! Valid: 7.5V or 11V~25V (step 1V)")
		self.bits_write(reg_val, 0x24, 4, 0)

	def read_vext_ovp(self):
		"""
		Read VEXT_CTRL (0x24) bit 3:0: VEXT_OVP
		Returns: actual voltage in V (0xF → 7.5V, others → 11V + reg_val × 1V)
		"""
		reg_val = self.bits_read(0x24, 4, 0)
		if reg_val == 0xF:
			return 7.5
		return 11.0 + reg_val


	# ==================== CTRL5 (0x25) ====================

	def read_vusb_dischg_ctrl1(self):
		"""
		Read CTRL5 (0x25) bit 7: VUSB_DISCHG_CTRL1
		Note: RW
		0: OFF (Default) | 1: ON
		"""
		return self.bits_read(0x25, 1, 7)

	def write_vusb_dischg_ctrl1(self, value):
		"""
		Write CTRL5 (0x25) bit 7: VUSB_DISCHG_CTRL1
		0: OFF (Default) | 1: ON
		"""
		self.bits_write(value, 0x25, 1, 7)

	def read_vusb_dischg_ctrl2(self):
		"""
		Read CTRL5 (0x25) bit 6: VUSB_DISCHG_CTRL2
		Note: RW (valid when VUSB_DISCHG_CTRL1=1)
		0: No effect on VUSB_DISCHG_CTRL1 (Default) | 1: Auto-clear VUSB_DISCHG_CTRL1 when VUSB < 0.3V
		"""
		return self.bits_read(0x25, 1, 6)

	def write_vusb_dischg_ctrl2(self, value):
		"""
		Write CTRL5 (0x25) bit 6: VUSB_DISCHG_CTRL2
		0: No effect (Default) | 1: Auto-clear when VUSB < 0.3V
		"""
		self.bits_write(value, 0x25, 1, 6)

	def read_vext_dischg_ctrl1(self):
		"""
		Read CTRL5 (0x25) bit 5: VEXT_DISCHG_CTRL1
		Note: RW
		0: OFF (Default) | 1: ON
		"""
		return self.bits_read(0x25, 1, 5)

	def write_vext_dischg_ctrl1(self, value):
		"""
		Write CTRL5 (0x25) bit 5: VEXT_DISCHG_CTRL1
		0: OFF (Default) | 1: ON
		"""
		self.bits_write(value, 0x25, 1, 5)

	def read_vext_dischg_ctrl2(self):
		"""
		Read CTRL5 (0x25) bit 4: VEXT_DISCHG_CTRL2
		Note: RW (valid when VEXT_DISCHG_CTRL1=1)
		0: No effect on VEXT_DISCHG_CTRL1 (Default) | 1: Auto-clear VEXT_DISCHG_CTRL1 when VEXT < 0.3V
		"""
		return self.bits_read(0x25, 1, 4)

	def write_vext_dischg_ctrl2(self, value):
		"""
		Write CTRL5 (0x25) bit 4: VEXT_DISCHG_CTRL2
		0: No effect (Default) | 1: Auto-clear when VEXT < 0.3V
		"""
		self.bits_write(value, 0x25, 1, 4)

	def read_drv1_short_det_dis(self):
		"""
		Read CTRL5 (0x25) bit 3: DRV1_SHORT_DET_DIS
		Note: RW
		0: Enable EXT1_DRV_SHORT detection (default) | 1: Disable
		"""
		return self.bits_read(0x25, 1, 3)

	def write_drv1_short_det_dis(self, value):
		"""
		Write CTRL5 (0x25) bit 3: DRV1_SHORT_DET_DIS
		0: Enable EXT1_DRV_SHORT detection (default) | 1: Disable
		"""
		self.bits_write(value, 0x25, 1, 3)

	def read_fet1_open_det_dis(self):
		"""
		Read CTRL5 (0x25) bit 2: FET1_OPEN_DET_DIS
		Note: RW
		0: Enable EXT1_FET_OPEN detection (default) | 1: Disable
		"""
		return self.bits_read(0x25, 1, 2)

	def write_fet1_open_det_dis(self, value):
		"""
		Write CTRL5 (0x25) bit 2: FET1_OPEN_DET_DIS
		0: Enable EXT1_FET_OPEN detection (default) | 1: Disable
		"""
		self.bits_write(value, 0x25, 1, 2)

	def read_fet_open(self):
		"""
		Read CTRL5 (0x25) bit 1:0: FET_OPEN
		Note: RW
		00: 0.5V (Default) | 01: 1V | 10: 2V | 11: 3V
		"""
		return self.bits_read(0x25, 2, 0)

	def write_fet_open(self, value):
		"""
		Write CTRL5 (0x25) bit 1:0: FET_OPEN
		00: 0.5V (Default) | 01: 1V | 10: 2V | 11: 3V
		"""
		self.bits_write(value, 0x25, 2, 0)

	# ==================== CTRL6 (0x26) ====================

	def read_drv2_short_det_dis(self):
		"""
		Read CTRL6 (0x26) bit 7: DRV2_SHORT_DET_DIS
		Note: RW
		0: Enable EXT2_DRV_SHORT detection (default) | 1: Disable
		"""
		return self.bits_read(0x26, 1, 7)

	def write_drv2_short_det_dis(self, value):
		"""
		Write CTRL6 (0x26) bit 7: DRV2_SHORT_DET_DIS
		0: Enable EXT2_DRV_SHORT detection (default) | 1: Disable
		"""
		self.bits_write(value, 0x26, 1, 7)

	def read_fet2_open_det_dis(self):
		"""
		Read CTRL6 (0x26) bit 6: FET2_OPEN_DET_DIS
		Note: RW
		0: Enable EXT2_FET_OPEN detection (default) | 1: Disable
		"""
		return self.bits_read(0x26, 1, 6)

	def write_fet2_open_det_dis(self, value):
		"""
		Write CTRL6 (0x26) bit 6: FET2_OPEN_DET_DIS
		0: Enable EXT2_FET_OPEN detection (default) | 1: Disable
		"""
		self.bits_write(value, 0x26, 1, 6)

	def read_cfly_short_det_ctrl(self):
		"""
		Read CTRL6 (0x26) bit 5:4: CFLY_SHORT_DET_CTRL
		Note: RW
		00: 100mV (default) | 01: 150mV | 10: 200mV | 11: 250mV
		"""
		return self.bits_read(0x26, 2, 4)

	def write_cfly_short_det_ctrl(self, value):
		"""
		Write CTRL6 (0x26) bit 5:4: CFLY_SHORT_DET_CTRL
		00: 100mV (default) | 01: 150mV | 10: 200mV | 11: 250mV
		"""
		self.bits_write(value, 0x26, 2, 4)

	def read_vdc_chg_en_falling(self):
		"""
		Read CTRL6 (0x26) bit 3:2: VDC_CHG_EN_FALLING
		Note: RW
		00: 2.9V (default) | 01: 2.8V | 10: 2.7V | 11: 2.6V
		"""
		return self.bits_read(0x26, 2, 2)

	def write_vdc_chg_en_falling(self, value):
		"""
		Write CTRL6 (0x26) bit 3:2: VDC_CHG_EN_FALLING
		00: 2.9V (default) | 01: 2.8V | 10: 2.7V | 11: 2.6V
		"""
		self.bits_write(value, 0x26, 2, 2)

	def read_vdc_chg_en_dg(self):
		"""
		Read CTRL6 (0x26) bit 1:0: VDC_CHG_EN_DG
		Note: RW
		00: 50us (default) | 01: 100us | 10: 400us | 11: 1600us
		"""
		return self.bits_read(0x26, 2, 0)

	def write_vdc_chg_en_dg(self, value):
		"""
		Write CTRL6 (0x26) bit 1:0: VDC_CHG_EN_DG
		00: 50us (default) | 01: 100us | 10: 400us | 11: 1600us
		"""
		self.bits_write(value, 0x26, 2, 0)

	# ==================== IIN_REG (0x27) ====================

	def write_iin_reg(self, current_ma):
		"""
		Write IIN_REG (0x27) bit 7:0: IIN_REG
		Args: current_ma — input current regulation threshold in mA
		Range: 0mA ~ 6000mA, step 50mA, clamped at 6000mA
		Raises: ValueError if current_ma < 0
		"""
		if current_ma < 0:
			raise ValueError(f"IIN_REG current {current_ma}mA out of range! Must be >= 0")
		reg_val = min(int(current_ma / 50), 0x78)
		self.bits_write(reg_val, 0x27, 8, 0)

	def read_iin_reg(self):
		"""
		Read IIN_REG (0x27) bit 7:0: IIN_REG
		Returns: input current regulation threshold in mA
		"""
		reg_val = self.bits_read(0x27, 8, 0)
		return reg_val * 50.0

	# ==================== VBAT_REG (0x28) ====================

	def write_vbat_reg(self, voltage):
		"""
		Write VBAT_REG (0x28) bit 7:0: VBAT_REG
		Args: voltage — battery regulation voltage in V
		Range: 3.84V ~ 5.115V, step 5mV
		Raises: ValueError if voltage out of range
		"""
		if not (3.84 <= voltage <= 5.115):
			raise ValueError(f"VBAT_REG voltage {voltage}V out of range! Valid: 3.84V ~ 5.115V")
		reg_val = int(round((voltage - 3.84) / 0.005))
		self.bits_write(reg_val, 0x28, 8, 0)

	def read_vbat_reg(self):
		"""
		Read VBAT_REG (0x28) bit 7:0: VBAT_REG
		Returns: battery regulation voltage in V
		"""
		reg_val = self.bits_read(0x28, 8, 0)
		return 3.84 + reg_val * 0.005

	
	# ==================== REG_CTRL (0x29) ====================

	def read_iin_reg_dis(self):
		"""
		Read REG_CTRL (0x29) bit 7: IIN_REG_DIS
		Note: RW
		0: Enable IIN_REG (default) | 1: Disable IIN_REG
		"""
		return self.bits_read(0x29, 1, 7)

	def write_iin_reg_dis(self, value):
		"""
		Write REG_CTRL (0x29) bit 7: IIN_REG_DIS
		0: Enable IIN_REG (default) | 1: Disable IIN_REG
		"""
		self.bits_write(value, 0x29, 1, 7)

	def read_vbat_reg_dis(self):
		"""
		Read REG_CTRL (0x29) bit 6: VBAT_REG_DIS
		Note: RW
		0: Enable VBAT_REG (default) | 1: Disable VBAT_REG
		"""
		return self.bits_read(0x29, 1, 6)

	def write_vbat_reg_dis(self, value):
		"""
		Write REG_CTRL (0x29) bit 6: VBAT_REG_DIS
		0: Enable VBAT_REG (default) | 1: Disable VBAT_REG
		"""
		self.bits_write(value, 0x29, 1, 6)

	def read_iin_ucp_cfg(self):
		"""
		Read REG_CTRL (0x29) bit 4: IIN_UCP_CFG
		Note: RW
		0: IIN_UCP only when IIN < IIN_UCP_FALL threshold and CP not in regulation (default)
		1: IIN_UCP once IIN < IIN_UCP_FALL threshold for t_IIN_UCP_FALLING
		"""
		return self.bits_read(0x29, 1, 4)

	def write_iin_ucp_cfg(self, value):
		"""
		Write REG_CTRL (0x29) bit 4: IIN_UCP_CFG
		0: Regulation-aware (default) | 1: Threshold-only
		"""
		self.bits_write(value, 0x29, 1, 4)

	def read_tdie_reg_dis(self):
		"""
		Read REG_CTRL (0x29) bit 3: TDIE_REG_DIS
		Note: RW
		0: Enable TDIE_REG (default) | 1: Disable TDIE_REG
		"""
		return self.bits_read(0x29, 1, 3)

	def write_tdie_reg_dis(self, value):
		"""
		Write REG_CTRL (0x29) bit 3: TDIE_REG_DIS
		0: Enable TDIE_REG (default) | 1: Disable TDIE_REG
		"""
		self.bits_write(value, 0x29, 1, 3)

	def read_iin_tdie_reg_interval(self):
		"""
		Read REG_CTRL (0x29) bit 2: IIN_TDIE_REG_INTERVAL
		Note: RW
		0: 200ms | 1: 500ms
		"""
		return self.bits_read(0x29, 1, 2)

	def write_iin_tdie_reg_interval(self, value):
		"""
		Write REG_CTRL (0x29) bit 2: IIN_TDIE_REG_INTERVAL
		0: 200ms | 1: 500ms
		"""
		self.bits_write(value, 0x29, 1, 2)

	def read_tdie_reg(self):
		"""
		Read REG_CTRL (0x29) bit 1:0: TDIE_REG
		Note: RW
		Die temperature regulation threshold | 00: 90°C | 01: 100°C (default) | 10: 110°C | 11: 120°C
		"""
		return self.bits_read(0x29, 2, 0)

	def write_tdie_reg(self, value):
		"""
		Write REG_CTRL (0x29) bit 1:0: TDIE_REG
		00: 90°C | 01: 100°C (default) | 10: 110°C | 11: 120°C
		"""
		self.bits_write(value, 0x29, 2, 0)

	# ==================== VBAT_OVP (0x2A) ====================

	def write_vbat_ovp(self, voltage):
		"""
		Write VBAT_OVP (0x2A) bit 7:0: VBAT_OVP
		Args: voltage — OVP threshold in V
		Range: 3.84V ~ 5.115V, step 5mV, default 4.5V
		Raises: ValueError if voltage out of range
		"""
		if not (3.84 <= voltage <= 5.115):
			raise ValueError(f"VBAT_OVP voltage {voltage}V out of range! Valid: 3.84V ~ 5.115V")
		reg_val = int(round((voltage - 3.84) / 0.005))
		self.bits_write(reg_val, 0x2A, 8, 0)

	def read_vbat_ovp(self):
		"""
		Read VBAT_OVP (0x2A) bit 7:0: VBAT_OVP
		Returns: OVP threshold in V
		"""
		reg_val = self.bits_read(0x2A, 8, 0)
		return 3.84 + reg_val * 0.005

	# ==================== VIN_OVP (0x2B) ====================

	def read_vin_ovp_dis(self):
		"""
		Read VIN_OVP (0x2B) bit 7: VIN_OVP_DIS
		Note: RW
		0: Enable VIN_OVP protection (default) | 1: Disable VIN_OVP protection
		"""
		return self.bits_read(0x2B, 1, 7)

	def write_vin_ovp_dis(self, value):
		"""
		Write VIN_OVP (0x2B) bit 7: VIN_OVP_DIS
		0: Enable VIN_OVP protection (default) | 1: Disable VIN_OVP protection
		"""
		self.bits_write(value, 0x2B, 1, 7)

	def write_vin_ovp(self, voltage):
		"""
		Write VIN_OVP (0x2B) bit 6:3: VIN_OVP
		Args: voltage — OVP threshold in V
		Formula: VIN_OVP = N × 3.75 + reg_val × 0.2 × N, where N depends on MODE (CTRL0 bits[2:0])
		Default: 9
		Raises: ValueError if voltage out of range
		"""
		mode = self.bits_read(0x1E, 4, 0)
		N = 4 - (mode & 0x3)
		reg_val = int(round((voltage / N - 3.75) / 0.2))
		if reg_val < 0 or reg_val > 15:
			raise ValueError(f"VIN_OVP voltage {voltage}V out of range for N={N}! Valid range: {N * 3.75:.2f}V ~ {N * (3.75 + 15 * 0.2):.2f}V")
		self.bits_write(reg_val, 0x2B, 4, 3)

	def read_vin_ovp(self):
		"""
		Read VIN_OVP (0x2B) bit 6:3: VIN_OVP
		Returns: OVP threshold in V (mode-dependent)
		"""
		mode = self.bits_read(0x1E, 4, 0)
		N = 4 - (mode & 0x3)
		reg_val = self.bits_read(0x2B, 4, 3)
		return N * (3.75 + reg_val * 0.2)

	def read_vin_pd_en(self):
		"""
		Read VIN_OVP (0x2B) bit 0: VIN_PD_EN
		Note: RW
		0: VIN pull-down disabled (default) | 1: VIN pull-down enabled
		"""
		return self.bits_read(0x2B, 1, 0)

	def write_vin_pd_en(self, value):
		"""
		Write VIN_OVP (0x2B) bit 0: VIN_PD_EN
		0: VIN pull-down disabled (default) | 1: VIN pull-down enabled
		"""
		self.bits_write(value, 0x2B, 1, 0)

	# ==================== VB_OUT_OVP (0x2C) ====================

	def read_vb_out_ovp_dis(self):
		"""
		Read VB_OUT_OVP (0x2C) bit 7: VB_OUT_OVP_DIS
		Note: RW
		0: Enable VB_OUT_OVP protection (default) | 1: Disable VB_OUT_OVP protection
		"""
		return self.bits_read(0x2C, 1, 7)

	def write_vb_out_ovp_dis(self, value):
		"""
		Write VB_OUT_OVP (0x2C) bit 7: VB_OUT_OVP_DIS
		0: Enable VB_OUT_OVP protection (default) | 1: Disable VB_OUT_OVP protection
		"""
		self.bits_write(value, 0x2C, 1, 7)

	def write_vb_out_ovp(self, voltage):
		"""
		Write VB_OUT_OVP (0x2C) bit 6:3: VB_OUT_OVP
		Args: voltage — OVP threshold in V
		Formula: VB_OUT_OVP = N × 3.75 + reg_val × 0.2 × N, same as VIN_OVP
		Default: 9
		Raises: ValueError if voltage out of range
		"""
		mode = self.bits_read(0x1E, 4, 0)
		N = 4 - (mode & 0x3)
		reg_val = int(round((voltage / N - 3.75) / 0.2))
		if reg_val < 0 or reg_val > 15:
			raise ValueError(f"VB_OUT_OVP voltage {voltage}V out of range for N={N}! Valid range: {N * 3.75:.2f}V ~ {N * (3.75 + 15 * 0.2):.2f}V")
		self.bits_write(reg_val, 0x2C, 4, 3)

	def read_vb_out_ovp(self):
		"""
		Read VB_OUT_OVP (0x2C) bit 6:3: VB_OUT_OVP
		Returns: OVP threshold in V (mode-dependent)
		"""
		mode = self.bits_read(0x1E, 4, 0)
		N = 4 - (mode & 0x3)
		reg_val = self.bits_read(0x2C, 4, 3)
		return N * (3.75 + reg_val * 0.2)

	def read_vb_out_pd_en(self):
		"""
		Read VB_OUT_OVP (0x2C) bit 0: VB_OUT_PD_EN
		Note: RW
		0: VB_OUT pull-down disabled (default) | 1: VB_OUT pull-down enabled
		"""
		return self.bits_read(0x2C, 1, 0)

	def write_vb_out_pd_en(self, value):
		"""
		Write VB_OUT_OVP (0x2C) bit 0: VB_OUT_PD_EN
		0: VB_OUT pull-down disabled (default) | 1: VB_OUT pull-down enabled
		"""
		self.bits_write(value, 0x2C, 1, 0)

	# ==================== IIN_OCP (0x2D) ====================

	def write_iin_ocp(self, current_ma):
		"""
		Write IIN_OCP (0x2D) bit 7:0: IIN_OCP
		Args: current_ma — OCP threshold in mA
		Range: 375mA ~ 6375mA, step 37.5mA, default 2250mA (0x3C)
		Raises: ValueError if current out of range
		"""
		if not (375 <= current_ma <= 6375):
			raise ValueError(f"IIN_OCP current {current_ma}mA out of range! Valid: 375mA ~ 6375mA")
		reg_val = int(round(current_ma / 37.5))
		self.bits_write(reg_val, 0x2D, 8, 0)

	def read_iin_ocp(self):
		"""
		Read IIN_OCP (0x2D) bit 7:0: IIN_OCP
		Returns: OCP threshold in mA
		"""
		reg_val = self.bits_read(0x2D, 8, 0)
		return reg_val * 37.5

	# ==================== VOUT/VDC_OVP (0x2E) ====================

	def read_vout_ovp_dis(self):
		"""
		Read VOUT/VDC_OVP (0x2E) bit 7: VOUT_OVP_DIS
		Note: RW
		0: Enable VOUT_OVP protection (default) | 1: Disable VOUT_OVP protection
		"""
		return self.bits_read(0x2E, 1, 7)

	def write_vout_ovp_dis(self, value):
		"""
		Write VOUT/VDC_OVP (0x2E) bit 7: VOUT_OVP_DIS
		0: Enable VOUT_OVP protection (default) | 1: Disable VOUT_OVP protection
		"""
		self.bits_write(value, 0x2E, 1, 7)

	def read_vout_ovp(self):
		"""
		Read VOUT/VDC_OVP (0x2E) bit 6:5: VOUT_OVP
		Note: RW
		00: 4.7V | 01: 4.9V | 10: 5.1V (default) | 11: 5.3V
		"""
		return self.bits_read(0x2E, 2, 5)

	def write_vout_ovp(self, value):
		"""
		Write VOUT/VDC_OVP (0x2E) bit 6:5: VOUT_OVP
		00: 4.7V | 01: 4.9V | 10: 5.1V (default) | 11: 5.3V
		"""
		self.bits_write(value, 0x2E, 2, 5)

	def read_vdc_ovp(self):
		"""
		Read VOUT/VDC_OVP (0x2E) bit 2:0: VDC_OVP
		Note: RW
		000: 0.5V | 001: 1V | 010: 1.5V | 011: 2V (default) | 100: 2.5V | 101: 3V | 110: 3.5V | 111: 4V
		"""
		return self.bits_read(0x2E, 3, 0)

	def write_vdc_ovp(self, value):
		"""
		Write VOUT/VDC_OVP (0x2E) bit 2:0: VDC_OVP
		000: 0.5V | 001: 1V | 010: 1.5V | 011: 2V (default) | 100: 2.5V | 101: 3V | 110: 3.5V | 111: 4V
		"""
		self.bits_write(value, 0x2E, 3, 0)

	# ==================== C1P2OUT_OVP (0x2F) ====================

	def read_c1p2out_ovp_dis(self):
		"""
		Read C1P2OUT_OVP (0x2F) bit 7: C1P2OUT_OVP_DIS
		Note: RW
		0: Enable C1P2OUT OVP (default) | 1: Disable C1P2OUT OVP
		"""
		return self.bits_read(0x2F, 1, 7)

	def write_c1p2out_ovp_dis(self, value):
		"""
		Write C1P2OUT_OVP (0x2F) bit 7: C1P2OUT_OVP_DIS
		0: Enable C1P2OUT OVP (default) | 1: Disable C1P2OUT OVP
		"""
		self.bits_write(value, 0x2F, 1, 7)

	def read_c1p2out_ovp_blk(self):
		"""
		Read C1P2OUT_OVP (0x2F) bit 6:5: C1P2OUT_OVP_BLK
		Note: RW
		00: 4 cycles | 01: 8 cycles | 10: 16 cycles | 11: 32 cycles (default)
		"""
		return self.bits_read(0x2F, 2, 5)

	def write_c1p2out_ovp_blk(self, value):
		"""
		Write C1P2OUT_OVP (0x2F) bit 6:5: C1P2OUT_OVP_BLK
		00: 4 cycles | 01: 8 cycles | 10: 16 cycles | 11: 32 cycles (default)
		"""
		self.bits_write(value, 0x2F, 2, 5)

	def read_c1p2out_ovp_dg(self):
		"""
		Read C1P2OUT_OVP (0x2F) bit 4:3: C1P2OUT_OVP_DG
		Note: RW
		00: no deglitch (default) | 01: 10ms | 10: 20ms | 11: 50ms
		"""
		return self.bits_read(0x2F, 2, 3)

	def write_c1p2out_ovp_dg(self, value):
		"""
		Write C1P2OUT_OVP (0x2F) bit 4:3: C1P2OUT_OVP_DG
		00: no deglitch (default) | 01: 10ms | 10: 20ms | 11: 50ms
		"""
		self.bits_write(value, 0x2F, 2, 3)

	def read_c1p2out_ovp(self):
		"""
		Read C1P2OUT_OVP (0x2F) bit 2:0: C1P2OUT_OVP
		Note: RW
		C1P2OUT OVP = reg_val / N × VOUT (N depends on MODE)
		000: 0.033×VOUT | 001: 0.082×VOUT | 010: 0.129×VOUT | 011: 0.164×VOUT (default)
		100: 0.200×VOUT | 101: 0.238×VOUT | 110: 0.280×VOUT | 111: 0.324×VOUT
		"""
		return self.bits_read(0x2F, 3, 0)

	def write_c1p2out_ovp(self, value):
		"""
		Write C1P2OUT_OVP (0x2F) bit 2:0: C1P2OUT_OVP
		000: 0.033×VOUT | 001: 0.082×VOUT | 010: 0.129×VOUT | 011: 0.164×VOUT (default)
		100: 0.200×VOUT | 101: 0.238×VOUT | 110: 0.280×VOUT | 111: 0.324×VOUT
		"""
		self.bits_write(value, 0x2F, 3, 0)

    # ==================== C1P2OUT_UVP (0x30) ====================

	def read_c1p2out_uvp_dis(self):
		"""
		Read C1P2OUT_UVP (0x30) bit 7: C1P2OUT_UVP_DIS
		Note: RW
		0: Enable C1P2OUT UVP (default) | 1: Disable C1P2OUT UVP
		"""
		return self.bits_read(0x30, 1, 7)

	def write_c1p2out_uvp_dis(self, value):
		"""
		Write C1P2OUT_UVP (0x30) bit 7: C1P2OUT_UVP_DIS
		0: Enable C1P2OUT UVP (default) | 1: Disable C1P2OUT UVP
		"""
		self.bits_write(value, 0x30, 1, 7)

	def read_c1p2out_uvp_blk(self):
		"""
		Read C1P2OUT_UVP (0x30) bit 6:5: C1P2OUT_UVP_BLK
		Note: RW
		00: 2 cycles (default) | 01: 4 cycles | 10: 8 cycles | 11: 16 cycles
		"""
		return self.bits_read(0x30, 2, 5)

	def write_c1p2out_uvp_blk(self, value):
		"""
		Write C1P2OUT_UVP (0x30) bit 6:5: C1P2OUT_UVP_BLK
		00: 2 cycles (default) | 01: 4 cycles | 10: 8 cycles | 11: 16 cycles
		"""
		self.bits_write(value, 0x30, 2, 5)

	def read_c1p2out_uvp_dg(self):
		"""
		Read C1P2OUT_UVP (0x30) bit 4:3: C1P2OUT_UVP_DG
		Note: RW
		00: no deglitch (default) | 01: 10ms | 10: 20ms | 11: 50ms
		"""
		return self.bits_read(0x30, 2, 3)

	def write_c1p2out_uvp_dg(self, value):
		"""
		Write C1P2OUT_UVP (0x30) bit 4:3: C1P2OUT_UVP_DG
		00: no deglitch (default) | 01: 10ms | 10: 20ms | 11: 50ms
		"""
		self.bits_write(value, 0x30, 2, 3)

	def read_c1p2out_uvp(self):
		"""
		Read C1P2OUT_UVP (0x30) bit 2:0: C1P2OUT_UVP
		Note: RW
		C1P2OUT UVP = reg_val / N × VOUT, N depends on MODE
		000: -0.015×VOUT | 001: -0.030×VOUT (default) | 010: -0.054×VOUT | 011: -0.077×VOUT
		100: -0.099×VOUT | 101: -0.119×VOUT | 110: -0.139×VOUT | 111: -0.165×VOUT
		"""
		return self.bits_read(0x30, 3, 0)

	def write_c1p2out_uvp(self, value):
		"""
		Write C1P2OUT_UVP (0x30) bit 2:0: C1P2OUT_UVP
		000: -0.015×VOUT | 001: -0.030×VOUT (default) | 010: -0.054×VOUT | 011: -0.077×VOUT
		100: -0.099×VOUT | 101: -0.119×VOUT | 110: -0.139×VOUT | 111: -0.165×VOUT
		"""
		self.bits_write(value, 0x30, 3, 0)

	# ==================== NTC_FLT (0x31) ====================

	def read_ntc_flt_dis(self):
		"""
		Read NTC_FLT (0x31) bit 7: NTC_FLT_DIS
		Note: RW
		0: Enable NTC_FLT protection (default) | 1: Disable NTC_FLT protection
		"""
		return self.bits_read(0x31, 1, 7)

	def write_ntc_flt_dis(self, value):
		"""
		Write NTC_FLT (0x31) bit 7: NTC_FLT_DIS
		0: Enable NTC_FLT protection (default) | 1: Disable NTC_FLT protection
		"""
		self.bits_write(value, 0x31, 1, 7)

	def write_ntc_flt(self, percentage):
		"""
		Write NTC_FLT (0x31) bit 5:0: NTC_FLT
		Args: percentage — NTC threshold as percentage of VIO (%)
		Range: 0% ~ 59.0688%, step 0.9376%, default 30.0032% (0x20)
		Raises: ValueError if percentage out of range
		"""
		if not (0 <= percentage <= 59.0688):
			raise ValueError(f"NTC_FLT {percentage}% out of range! Valid: 0% ~ 59.0688%")
		reg_val = int(round(percentage / 0.9376))
		self.bits_write(reg_val, 0x31, 6, 0)

	def read_ntc_flt(self):
		"""
		Read NTC_FLT (0x31) bit 5:0: NTC_FLT
		Returns: NTC threshold as percentage of VIO (%)
		"""
		reg_val = self.bits_read(0x31, 6, 0)
		return reg_val * 0.9376

	# ==================== PROTECT_DIS (0x32) ====================

	def read_iin_ocp_dis(self):
		"""
		Read PROTECT_DIS (0x32) bit 7: IIN_OCP_DIS
		Note: RW
		0: Enable IIN_OCP protection (default) | 1: Disable IIN_OCP protection
		"""
		return self.bits_read(0x32, 1, 7)

	def write_iin_ocp_dis(self, value):
		"""
		Write PROTECT_DIS (0x32) bit 7: IIN_OCP_DIS
		0: Enable IIN_OCP protection (default) | 1: Disable IIN_OCP protection
		"""
		self.bits_write(value, 0x32, 1, 7)

	def read_pin_diag_fail_dis(self):
		"""
		Read PROTECT_DIS (0x32) bit 6: PIN_DIAG_FAIL_DIS
		Note: RW
		0: Enable PIN_DIAG_FAIL protection (default) | 1: Disable PIN_DIAG_FAIL protection
		"""
		return self.bits_read(0x32, 1, 6)

	def write_pin_diag_fail_dis(self, value):
		"""
		Write PROTECT_DIS (0x32) bit 6: PIN_DIAG_FAIL_DIS
		0: Enable PIN_DIAG_FAIL protection (default) | 1: Disable PIN_DIAG_FAIL protection
		"""
		self.bits_write(value, 0x32, 1, 6)

	def read_cfly_open_dis(self):
		"""
		Read PROTECT_DIS (0x32) bit 5: CFLY_OPEN_DIS
		Note: RW
		0: Enable CFLY_OPEN protection (default) | 1: Disable CFLY_OPEN protection
		"""
		return self.bits_read(0x32, 1, 5)

	def write_cfly_open_dis(self, value):
		"""
		Write PROTECT_DIS (0x32) bit 5: CFLY_OPEN_DIS
		0: Enable CFLY_OPEN protection (default) | 1: Disable CFLY_OPEN protection
		"""
		self.bits_write(value, 0x32, 1, 5)

	def read_cfly_short_dis(self):
		"""
		Read PROTECT_DIS (0x32) bit 4: CFLY_SHORT_DIS
		Note: RW
		0: Enable CFLY_SHORT protection (default) | 1: Disable CFLY_SHORT protection
		"""
		return self.bits_read(0x32, 1, 4)

	def write_cfly_short_dis(self, value):
		"""
		Write PROTECT_DIS (0x32) bit 4: CFLY_SHORT_DIS
		0: Enable CFLY_SHORT protection (default) | 1: Disable CFLY_SHORT protection
		"""
		self.bits_write(value, 0x32, 1, 4)

	def read_bst_fail_dis(self):
		"""
		Read PROTECT_DIS (0x32) bit 3: BST_FAIL_DIS
		Note: RW
		0: Enable BST_FAIL protection (default) | 1: Disable BST_FAIL protection
		"""
		return self.bits_read(0x32, 1, 3)

	def write_bst_fail_dis(self, value):
		"""
		Write PROTECT_DIS (0x32) bit 3: BST_FAIL_DIS
		0: Enable BST_FAIL protection (default) | 1: Disable BST_FAIL protection
		"""
		self.bits_write(value, 0x32, 1, 3)

	def read_tshut_dis(self):
		"""
		Read PROTECT_DIS (0x32) bit 2: TSHUT_DIS
		Note: RW
		0: Enable thermal shutdown protection (default) | 1: Disable thermal shutdown protection
		"""
		return self.bits_read(0x32, 1, 2)

	def write_tshut_dis(self, value):
		"""
		Write PROTECT_DIS (0x32) bit 2: TSHUT_DIS
		0: Enable thermal shutdown protection (default) | 1: Disable thermal shutdown protection
		"""
		self.bits_write(value, 0x32, 1, 2)

	def read_vbat_ovp_dis(self):
		"""
		Read PROTECT_DIS (0x32) bit 1: VBAT_OVP_DIS
		Note: RW
		0: Enable VBAT_OVP protection (default) | 1: Disable VBAT_OVP protection
		"""
		return self.bits_read(0x32, 1, 1)

	def write_vbat_ovp_dis(self, value):
		"""
		Write PROTECT_DIS (0x32) bit 1: VBAT_OVP_DIS
		0: Enable VBAT_OVP protection (default) | 1: Disable VBAT_OVP protection
		"""
		self.bits_write(value, 0x32, 1, 1)

	def read_iin_ucp_dis(self):
		"""
		Read PROTECT_DIS (0x32) bit 0: IIN_UCP_DIS
		Note: RW
		0: Enable IIN_UCP protection (default) | 1: Disable IIN_UCP protection
		"""
		return self.bits_read(0x32, 1, 0)

	def write_iin_ucp_dis(self, value):
		"""
		Write PROTECT_DIS (0x32) bit 0: IIN_UCP_DIS
		0: Enable IIN_UCP protection (default) | 1: Disable IIN_UCP protection
		"""
		self.bits_write(value, 0x32, 1, 0)

	# ==================== DEGLITCH_CTRL0 (0x33) ====================

	def read_vb_in_connect_vin(self):
		"""
		Read DEGLITCH_CTRL0 (0x33) bit 7: VB_IN_CONNECT_VIN
		Note: RW
		0: VB_IN not connect to VIN (default) | 1: VB_IN connect to VIN (QB2 works as OVP_FET in manual mode)
		"""
		return self.bits_read(0x33, 1, 7)

	def write_vb_in_connect_vin(self, value):
		"""
		Write DEGLITCH_CTRL0 (0x33) bit 7: VB_IN_CONNECT_VIN
		0: Not connected (default) | 1: Connected
		"""
		self.bits_write(value, 0x33, 1, 7)

	def read_iin_ocp_dg_set(self):
		"""
		Read DEGLITCH_CTRL0 (0x33) bit 5:4: IIN_OCP_DG_SET
		Note: RW
		IIN OCP deglitch time | 00: no deglitch | 01: 80us (default) | 10: 320us | 11: 5ms
		"""
		return self.bits_read(0x33, 2, 4)

	def write_iin_ocp_dg_set(self, value):
		"""
		Write DEGLITCH_CTRL0 (0x33) bit 5:4: IIN_OCP_DG_SET
		00: no deglitch | 01: 80us (default) | 10: 320us | 11: 5ms
		"""
		self.bits_write(value, 0x33, 2, 4)

	def read_vbat_ovp_dg_set(self):
		"""
		Read DEGLITCH_CTRL0 (0x33) bit 3:2: VBAT_OVP_DG_SET
		Note: RW
		VBAT OVP deglitch time | 00: no deglitch (default) | 01: 80us | 10: 320us | 11: 5ms
		"""
		return self.bits_read(0x33, 2, 2)

	def write_vbat_ovp_dg_set(self, value):
		"""
		Write DEGLITCH_CTRL0 (0x33) bit 3:2: VBAT_OVP_DG_SET
		00: no deglitch (default) | 01: 80us | 10: 320us | 11: 5ms
		"""
		self.bits_write(value, 0x33, 2, 2)

	def read_vout_ovp_dg_set(self):
		"""
		Read DEGLITCH_CTRL0 (0x33) bit 0: VOUT_OVP_DG_SET
		Note: RW
		0: no deglitch (default) | 1: 80us
		"""
		return self.bits_read(0x33, 1, 0)

	def write_vout_ovp_dg_set(self, value):
		"""
		Write DEGLITCH_CTRL0 (0x33) bit 0: VOUT_OVP_DG_SET
		0: no deglitch (default) | 1: 80us
		"""
		self.bits_write(value, 0x33, 1, 0)

	# ==================== DEGLITCH_CTRL1 (0x34) ====================

	def read_vusb_ovp_dg_set(self):
		"""
		Read DEGLITCH_CTRL1 (0x34) bit 7:6: VUSB_OVP_DG_SET
		Note: RW
		VUSB OVP deglitch time | 00: no deglitch (default) | 01: 80us | 10: 20ms | 11: 80ms
		"""
		return self.bits_read(0x34, 2, 6)

	def write_vusb_ovp_dg_set(self, value):
		"""
		Write DEGLITCH_CTRL1 (0x34) bit 7:6: VUSB_OVP_DG_SET
		00: no deglitch (default) | 01: 80us | 10: 20ms | 11: 80ms
		"""
		self.bits_write(value, 0x34, 2, 6)

	def read_vext_ovp_dg_set(self):
		"""
		Read DEGLITCH_CTRL1 (0x34) bit 5:4: VEXT_OVP_DG_SET
		Note: RW
		VEXT OVP deglitch time | 00: no deglitch (default) | 01: 80us | 10: 20ms | 11: 80ms
		"""
		return self.bits_read(0x34, 2, 4)

	def write_vext_ovp_dg_set(self, value):
		"""
		Write DEGLITCH_CTRL1 (0x34) bit 5:4: VEXT_OVP_DG_SET
		00: no deglitch (default) | 01: 80us | 10: 20ms | 11: 80ms
		"""
		self.bits_write(value, 0x34, 2, 4)

	def read_vin_ovp_dg_set(self):
		"""
		Read DEGLITCH_CTRL1 (0x34) bit 3: VIN_OVP_DG_SET
		Note: RW
		0: no deglitch (default) | 1: 80us
		"""
		return self.bits_read(0x34, 1, 3)

	def write_vin_ovp_dg_set(self, value):
		"""
		Write DEGLITCH_CTRL1 (0x34) bit 3: VIN_OVP_DG_SET
		0: no deglitch (default) | 1: 80us
		"""
		self.bits_write(value, 0x34, 1, 3)

	def read_vb_out_ovp_dg_set(self):
		"""
		Read DEGLITCH_CTRL1 (0x34) bit 2: VB_OUT_OVP_DG_SET
		Note: RW
		0: no deglitch (default) | 1: 80us
		"""
		return self.bits_read(0x34, 1, 2)

	def write_vb_out_ovp_dg_set(self, value):
		"""
		Write DEGLITCH_CTRL1 (0x34) bit 2: VB_OUT_OVP_DG_SET
		0: no deglitch (default) | 1: 80us
		"""
		self.bits_write(value, 0x34, 1, 2)

	def read_iin_ucp_fall_dg_set(self):
		"""
		Read DEGLITCH_CTRL1 (0x34) bit 1:0: IIN_UCP_FALL_DG_SET
		Note: RW
		IIN_UCP_FALL deglitch time | 00: 1ms | 01: 5ms | 10: 20ms (default) | 11: 50ms
		"""
		return self.bits_read(0x34, 2, 0)

	def write_iin_ucp_fall_dg_set(self, value):
		"""
		Write DEGLITCH_CTRL1 (0x34) bit 1:0: IIN_UCP_FALL_DG_SET
		00: 1ms | 01: 5ms | 10: 20ms (default) | 11: 50ms
		"""
		self.bits_write(value, 0x34, 2, 0)	

	# ==================== ADC_CTRL (0x35) ====================

	def read_adc_en(self):
		"""
		Read ADC_CTRL (0x35) bit 7: ADC_EN
		Note: RW
		0: ADC Disabled (default) | 1: ADC Enabled
		"""
		return self.bits_read(0x35, 1, 7)

	def write_adc_en(self, value):
		"""
		Write ADC_CTRL (0x35) bit 7: ADC_EN
		0: ADC Disabled (default) | 1: ADC Enabled
		"""
		self.bits_write(value, 0x35, 1, 7)

	def read_adc_rate(self):
		"""
		Read ADC_CTRL (0x35) bit 6: ADC_RATE
		Note: RW
		0: Continuous conversion (default) | 1: One-shot
		"""
		return self.bits_read(0x35, 1, 6)

	def write_adc_rate(self, value):
		"""
		Write ADC_CTRL (0x35) bit 6: ADC_RATE
		0: Continuous conversion (default) | 1: One-shot
		"""
		self.bits_write(value, 0x35, 1, 6)

	def read_adc_freeze(self):
		"""
		Read ADC_CTRL (0x35) bit 5: ADC_FREEZE
		Note: RW (continuous mode only)
		0: ADC conversion continues (default) | 1: ADC conversion freeze
		"""
		return self.bits_read(0x35, 1, 5)

	def write_adc_freeze(self, value):
		"""
		Write ADC_CTRL (0x35) bit 5: ADC_FREEZE
		0: ADC conversion continues (default) | 1: ADC conversion freeze
		"""
		self.bits_write(value, 0x35, 1, 5)

	def read_iin_adc_dis(self):
		"""
		Read ADC_CTRL (0x35) bit 1: IIN_ADC_DIS
		Note: RW
		0: Enable IIN ADC conversion (default) | 1: Disable IIN ADC conversion
		"""
		return self.bits_read(0x35, 1, 1)

	def write_iin_adc_dis(self, value):
		"""
		Write ADC_CTRL (0x35) bit 1: IIN_ADC_DIS
		0: Enable IIN ADC conversion (default) | 1: Disable IIN ADC conversion
		"""
		self.bits_write(value, 0x35, 1, 1)

	def read_vin_adc_dis(self):
		"""
		Read ADC_CTRL (0x35) bit 0: VIN_ADC_DIS
		Note: RW
		0: Enable VIN ADC conversion (default) | 1: Disable VIN ADC conversion
		"""
		return self.bits_read(0x35, 1, 0)

	def write_vin_adc_dis(self, value):
		"""
		Write ADC_CTRL (0x35) bit 0: VIN_ADC_DIS
		0: Enable VIN ADC conversion (default) | 1: Disable VIN ADC conversion
		"""
		self.bits_write(value, 0x35, 1, 0)

	# ==================== ADC_FN_DISABLE (0x36) ====================

	def read_vb_out_adc_dis(self):
		"""
		Read ADC_FN_DISABLE (0x36) bit 7: VB_OUT_ADC_DIS
		Note: RW
		0: Enable VB_OUT ADC conversion (default) | 1: Disable VB_OUT ADC conversion
		"""
		return self.bits_read(0x36, 1, 7)

	def write_vb_out_adc_dis(self, value):
		"""
		Write ADC_FN_DISABLE (0x36) bit 7: VB_OUT_ADC_DIS
		0: Enable VB_OUT ADC conversion (default) | 1: Disable VB_OUT ADC conversion
		"""
		self.bits_write(value, 0x36, 1, 7)

	def read_vusb_adc_dis(self):
		"""
		Read ADC_FN_DISABLE (0x36) bit 6: VUSB_ADC_DIS
		Note: RW
		0: Enable VUSB ADC conversion (default) | 1: Disable VUSB ADC conversion
		"""
		return self.bits_read(0x36, 1, 6)

	def write_vusb_adc_dis(self, value):
		"""
		Write ADC_FN_DISABLE (0x36) bit 6: VUSB_ADC_DIS
		0: Enable VUSB ADC conversion (default) | 1: Disable VUSB ADC conversion
		"""
		self.bits_write(value, 0x36, 1, 6)

	def read_vext_adc_dis(self):
		"""
		Read ADC_FN_DISABLE (0x36) bit 5: VEXT_ADC_DIS
		Note: RW
		0: Enable VEXT ADC conversion (default) | 1: Disable VEXT ADC conversion
		"""
		return self.bits_read(0x36, 1, 5)

	def write_vext_adc_dis(self, value):
		"""
		Write ADC_FN_DISABLE (0x36) bit 5: VEXT_ADC_DIS
		0: Enable VEXT ADC conversion (default) | 1: Disable VEXT ADC conversion
		"""
		self.bits_write(value, 0x36, 1, 5)

	def read_vout_adc_dis(self):
		"""
		Read ADC_FN_DISABLE (0x36) bit 4: VOUT_ADC_DIS
		Note: RW
		0: Enable VOUT ADC conversion (default) | 1: Disable VOUT ADC conversion
		"""
		return self.bits_read(0x36, 1, 4)

	def write_vout_adc_dis(self, value):
		"""
		Write ADC_FN_DISABLE (0x36) bit 4: VOUT_ADC_DIS
		0: Enable VOUT ADC conversion (default) | 1: Disable VOUT ADC conversion
		"""
		self.bits_write(value, 0x36, 1, 4)

	def read_vbat_adc_dis(self):
		"""
		Read ADC_FN_DISABLE (0x36) bit 3: VBAT_ADC_DIS
		Note: RW
		0: Enable VBAT ADC conversion (default) | 1: Disable VBAT ADC conversion
		"""
		return self.bits_read(0x36, 1, 3)

	def write_vbat_adc_dis(self, value):
		"""
		Write ADC_FN_DISABLE (0x36) bit 3: VBAT_ADC_DIS
		0: Enable VBAT ADC conversion (default) | 1: Disable VBAT ADC conversion
		"""
		self.bits_write(value, 0x36, 1, 3)

	def read_tdie_adc_dis(self):
		"""
		Read ADC_FN_DISABLE (0x36) bit 2: TDIE_ADC_DIS
		Note: RW
		0: Enable TDIE ADC conversion (default) | 1: Disable TDIE ADC conversion
		"""
		return self.bits_read(0x36, 1, 2)

	def write_tdie_adc_dis(self, value):
		"""
		Write ADC_FN_DISABLE (0x36) bit 2: TDIE_ADC_DIS
		0: Enable TDIE ADC conversion (default) | 1: Disable TDIE ADC conversion
		"""
		self.bits_write(value, 0x36, 1, 2)

	def read_c1p_adc_dis(self):
		"""
		Read ADC_FN_DISABLE (0x36) bit 1: C1P_ADC_DIS
		Note: RW
		0: Enable C1P ADC conversion (default) | 1: Disable C1P ADC conversion
		"""
		return self.bits_read(0x36, 1, 1)

	def write_c1p_adc_dis(self, value):
		"""
		Write ADC_FN_DISABLE (0x36) bit 1: C1P_ADC_DIS
		0: Enable C1P ADC conversion (default) | 1: Disable C1P ADC conversion
		"""
		self.bits_write(value, 0x36, 1, 1)

	def read_ntc_adc_dis(self):
		"""
		Read ADC_FN_DISABLE (0x36) bit 0: NTC_ADC_DIS
		Note: RW
		0: Enable NTC ADC conversion (default) | 1: Disable NTC ADC conversion
		"""
		return self.bits_read(0x36, 1, 0)

	def write_ntc_adc_dis(self, value):
		"""
		Write ADC_FN_DISABLE (0x36) bit 0: NTC_ADC_DIS
		0: Enable NTC ADC conversion (default) | 1: Disable NTC ADC conversion
		"""
		self.bits_write(value, 0x36, 1, 0)

    # ==================== ADC Readback (0x37 ~ 0x4A) ====================
    # All ADC readback registers are Read-Only.
    # 12-bit value = (ADC1[3:0] << 8) | ADC0[7:0]
    # TDIE is 9-bit: (TDIE_ADC1[0] << 8) | TDIE_ADC0[7:0]

	def read_iin_adc(self):
		"""
		Read IIN_ADC1 (0x37) + IIN_ADC0 (0x38): IIN ADC (12-bit)
		Returns: IIN current in mA (LSB: 1.875mA)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x37, 4, 0)
		lo = self.bits_read(0x38, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 1.875

	def read_vin_adc(self):
		"""
		Read VIN_ADC1 (0x39) + VIN_ADC0 (0x3A): VIN ADC (12-bit)
		Returns: VIN voltage in V (LSB: 6.25mV)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x39, 4, 0)
		lo = self.bits_read(0x3A, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 0.00625

	def read_vb_out_adc(self):
		"""
		Read VB_OUT_ADC1 (0x3B) + VB_OUT_ADC0 (0x3C): VB_OUT ADC (12-bit)
		Returns: VB_OUT voltage in V (LSB: 6.25mV)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x3B, 4, 0)
		lo = self.bits_read(0x3C, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 0.00625

	def read_vusb_adc(self):
		"""
		Read VUSB_ADC1 (0x3D) + VUSB_ADC0 (0x3E): VUSB ADC (12-bit)
		Returns: VUSB voltage in V (LSB: 6.25mV)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x3D, 4, 0)
		lo = self.bits_read(0x3E, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 0.00625

	def read_vext_adc(self):
		"""
		Read VEXT_ADC1 (0x3F) + VEXT_ADC0 (0x40): VEXT ADC (12-bit)
		Returns: VEXT voltage in V (LSB: 6.25mV)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x3F, 4, 0)
		lo = self.bits_read(0x40, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 0.00625

	def read_vout_adc(self):
		"""
		Read VOUT_ADC1 (0x41) + VOUT_ADC0 (0x42): VOUT ADC (12-bit)
		Returns: VOUT voltage in V (LSB: 1.25mV)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x41, 4, 0)
		lo = self.bits_read(0x42, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 0.00125

	def read_vbat_adc(self):
		"""
		Read VBAT_ADC1 (0x43) + VBAT_ADC0 (0x44): VBAT ADC (12-bit)
		Returns: VBAT voltage in V (LSB: 1.25mV)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x43, 4, 0)
		lo = self.bits_read(0x44, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 0.00125

	def read_c1p_adc(self):
		"""
		Read C1P_ADC1 (0x45) + C1P_ADC0 (0x46): C1P ADC (12-bit)
		Returns: C1P voltage in V (LSB: 6.25mV)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x45, 4, 0)
		lo = self.bits_read(0x46, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 0.00625

	def read_ntc_adc(self):
		"""
		Read NTC_ADC1 (0x47) + NTC_ADC0 (0x48): NTC ADC (12-bit)
		Returns: NTC pin voltage as percentage of VIO (%)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x47, 4, 0)
		lo = self.bits_read(0x48, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 0.01465

	def read_tdie_adc(self):
		"""
		Read TDIE_ADC1 (0x49) + TDIE_ADC0 (0x4A): TDIE ADC (9-bit)
		Returns: Die temperature in °C (LSB: 0.5°C)
		"""
		self.write_adc_freeze(1)
		time.sleep(0.01)
		hi = self.bits_read(0x49, 1, 0)
		lo = self.bits_read(0x4A, 8, 0)
		self.write_adc_freeze(0)
		raw = (hi << 8) | lo
		return raw * 0.5


# ==================== ZVS_CTRL (0x4B) ====================

	def read_reg_q8_rcp(self):
		"""
		Read ZVS_CTRL (0x4B) bit 7: REG_Q8_RCP
		Q8 RCP threshold
		"""
		return self.bits_read(0x4B, 1, 7)

	def write_reg_q8_rcp(self, value):
		"""
		Write ZVS_CTRL (0x4B) bit 7: REG_Q8_RCP
		Q8 RCP threshold
		"""
		self.bits_write(value, 0x4B, 1, 7)

	def read_reg_q8_rcp_dis(self):
		"""
		Read ZVS_CTRL (0x4B) bit 6: REG_Q8_RCP_DIS
		0: Q8_RCP enable (default) | 1: Q8_RCP disable
		"""
		return self.bits_read(0x4B, 1, 6)

	def write_reg_q8_rcp_dis(self, value):
		"""
		Write ZVS_CTRL (0x4B) bit 6: REG_Q8_RCP_DIS
		0: Q8_RCP enable (default) | 1: Q8_RCP disable
		"""
		self.bits_write(value, 0x4B, 1, 6)

	def read_reg_vdcmode_always_en_q9(self):
		"""
		Read ZVS_CTRL (0x4B) bit 5: REG_VDCMODE_ALWAYSenQ9
		0: Q9 turn on in VDC mode | 1: Q9 turn off in VDC mode
		"""
		return self.bits_read(0x4B, 1, 5)

	def write_reg_vdcmode_always_en_q9(self, value):
		"""
		Write ZVS_CTRL (0x4B) bit 5: REG_VDCMODE_ALWAYSenQ9
		0: Q9 turn on in VDC mode | 1: Q9 turn off in VDC mode
		"""
		self.bits_write(value, 0x4B, 1, 5)

	def read_vext_usb_pd_res(self):
		"""
		Read ZVS_CTRL (0x4B) bit 1: VEXT/USB_PD_RES
		0: 1kOhm | 1: 100Ohm
		"""
		return self.bits_read(0x4B, 1, 1)

	def write_vext_usb_pd_res(self, value):
		"""
		Write ZVS_CTRL (0x4B) bit 1: VEXT/USB_PD_RES
		0: 1kOhm | 1: 100Ohm
		"""
		self.bits_write(value, 0x4B, 1, 1)

	def read_cs_mode(self):
		"""
		Read ZVS_CTRL (0x4B) bit 0: CS_MODE
		0: CS mode | 1: normal mode
		"""
		return self.bits_read(0x4B, 1, 0)

	def write_cs_mode(self, value):
		"""
		Write ZVS_CTRL (0x4B) bit 0: CS_MODE
		0: CS mode | 1: normal mode
		"""
		self.bits_write(value, 0x4B, 1, 0)

	# ==================== CTRL6 (0x4C) ====================

	def read_vout_th_rev_low(self):
		"""
		Read CTRL6 (0x4C) bit 7: VOUT_TH_REV_LOW
		"""
		return self.bits_read(0x4C, 1, 7)

	def write_vout_th_rev_low(self, value):
		"""
		Write CTRL6 (0x4C) bit 7: VOUT_TH_REV_LOW
		"""
		self.bits_write(value, 0x4C, 1, 7)

	def read_acdrv_ss(self):
		"""
		Read CTRL6 (0x4C) bit 6:5: ACDRV_SS
		"""
		return self.bits_read(0x4C, 2, 5)

	def write_acdrv_ss(self, value):
		"""
		Write CTRL6 (0x4C) bit 6:5: ACDRV_SS
		"""
		self.bits_write(value, 0x4C, 2, 5)

	def read_qb_fast_ss(self):
		"""
		Read CTRL6 (0x4C) bit 4:3: QB_FAST_SS
		"""
		return self.bits_read(0x4C, 2, 3)

	def write_qb_fast_ss(self, value):
		"""
		Write CTRL6 (0x4C) bit 4:3: QB_FAST_SS
		"""
		self.bits_write(value, 0x4C, 2, 3)

	def read_vo12out_uvp_dis(self):
		"""
		Read CTRL6 (0x4C) bit 2: VO12OUT_UVP_DIS
		"""
		return self.bits_read(0x4C, 1, 2)

	def write_vo12out_uvp_dis(self, value):
		"""
		Write CTRL6 (0x4C) bit 2: VO12OUT_UVP_DIS
		"""
		self.bits_write(value, 0x4C, 1, 2)

	def read_vo12out_uvp(self):
		"""
		Read CTRL6 (0x4C) bit 1:0: VO12OUT_UVP
		00: -0.015*VOUT | 01: -0.03*VOUT | 10: -0.0985*VOUT | 11: 0.165*VOUT
		"""
		return self.bits_read(0x4C, 2, 0)

	def write_vo12out_uvp(self, value):
		"""
		Write CTRL6 (0x4C) bit 1:0: VO12OUT_UVP
		00: -0.015*VOUT | 01: -0.03*VOUT | 10: -0.0985*VOUT | 11: 0.165*VOUT
		"""
		self.bits_write(value, 0x4C, 2, 0)

	# ==================== CTRL7 (0x4D) ====================

	def read_mos_ocp_dis(self):
		"""
		Read CTRL7 (0x4D) bit 7: MOS_OCP_DIS
		"""
		return self.bits_read(0x4D, 1, 7)

	def write_mos_ocp_dis(self, value):
		"""
		Write CTRL7 (0x4D) bit 7: MOS_OCP_DIS
		"""
		self.bits_write(value, 0x4D, 1, 7)

	def read_fast_protection_blanking(self):
		"""
		Read CTRL7 (0x4D) bit 6:5: FAST_PROTECTION_BLANKING
		00: 0 cycles | 01: 4 cycles | 10: 8 cycles | 11: 16 cycles
		"""
		return self.bits_read(0x4D, 2, 5)

	def write_fast_protection_blanking(self, value):
		"""
		Write CTRL7 (0x4D) bit 6:5: FAST_PROTECTION_BLANKING
		00: 0 cycles | 01: 4 cycles | 10: 8 cycles | 11: 16 cycles
		"""
		self.bits_write(value, 0x4D, 2, 5)

	def read_reg_q2_ocp(self):
		"""
		Read CTRL7 (0x4D) bit 4: REG_Q2_OCP
		"""
		return self.bits_read(0x4D, 1, 4)

	def write_reg_q2_ocp(self, value):
		"""
		Write CTRL7 (0x4D) bit 4: REG_Q2_OCP
		"""
		self.bits_write(value, 0x4D, 1, 4)

	def read_bst_fast_protection(self):
		"""
		Read CTRL7 (0x4D) bit 3: BST_FAST_PROTECTION
		0: BST short fast protection | 1: BST short slow protection
		"""
		return self.bits_read(0x4D, 1, 3)

	def write_bst_fast_protection(self, value):
		"""
		Write CTRL7 (0x4D) bit 3: BST_FAST_PROTECTION
		0: BST short fast protection | 1: BST short slow protection
		"""
		self.bits_write(value, 0x4D, 1, 3)

	def read_vout_th_chg_low(self):
		"""
		Read CTRL7 (0x4D) bit 0: VOUT_TH_CHG_LOW
		"""
		return self.bits_read(0x4D, 1, 0)

	def write_vout_th_chg_low(self, value):
		"""
		Write CTRL7 (0x4D) bit 0: VOUT_TH_CHG_LOW
		"""
		self.bits_write(value, 0x4D, 1, 0)

	# ==================== QB_RCP_CTRL (0x4E) ====================

	def read_dis_qb_rcp(self):
		"""
		Read QB_RCP_CTRL (0x4E) bit 7: DIS_QB_RCP
		"""
		return self.bits_read(0x4E, 1, 7)

	def write_dis_qb_rcp(self, value):
		"""
		Write QB_RCP_CTRL (0x4E) bit 7: DIS_QB_RCP
		"""
		self.bits_write(value, 0x4E, 1, 7)

	def read_qb_rcp(self):
		"""
		Read QB_RCP_CTRL (0x4E) bit 6:5: QB_RCP
		"""
		return self.bits_read(0x4E, 2, 5)

	def write_qb_rcp(self, value):
		"""
		Write QB_RCP_CTRL (0x4E) bit 6:5: QB_RCP
		"""
		self.bits_write(value, 0x4E, 2, 5)

	def read_qb_rcp_flag(self):
		"""
		Read QB_RCP_CTRL (0x4E) bit 4: QB_RCP_FLAG
		"""
		return self.bits_read(0x4E, 1, 4)

	def read_qb_rcp_mask(self):
		"""
		Read QB_RCP_CTRL (0x4E) bit 3: QB_RCP_MASK
		"""
		return self.bits_read(0x4E, 1, 3)

	def write_qb_rcp_mask(self, value):
		"""
		Write QB_RCP_CTRL (0x4E) bit 3: QB_RCP_MASK
		"""
		self.bits_write(value, 0x4E, 1, 3)

	def read_vb_out_chg_en_dis(self):
		"""
		Read QB_RCP_CTRL (0x4E) bit 2: VB_OUT_CHG_EN_DIS
		0: VB_OUT_TH_CHG disable | 1: VB_OUT_TH_CHG enable
		"""
		return self.bits_read(0x4E, 1, 2)

	def write_vb_out_chg_en_dis(self, value):
		"""
		Write QB_RCP_CTRL (0x4E) bit 2: VB_OUT_CHG_EN_DIS
		0: VB_OUT_TH_CHG disable | 1: VB_OUT_TH_CHG enable
		"""
		self.bits_write(value, 0x4E, 1, 2)

	# ==================== VOUT_DROP_CTRL (0x4F) ====================

	def read_vout_drop_ctrl(self):
		"""
		Read VOUT_DROP_CTRL (0x4F) bit 7: VOUT_DROP_CTRL
		"""
		return self.bits_read(0x4F, 1, 7)

	def write_vout_drop_ctrl(self, value):
		"""
		Write VOUT_DROP_CTRL (0x4F) bit 7: VOUT_DROP_CTRL
		"""
		self.bits_write(value, 0x4F, 1, 7)

	def read_vout_drop_fast_drop_flag(self):
		"""
		Read VOUT_DROP_CTRL (0x4F) bit 6: VOUT_DROP_FAST_DROP_FLAG
		"""
		return self.bits_read(0x4F, 1, 6)

	def read_vout_drop_fast_drop_mask(self):
		"""
		Read VOUT_DROP_CTRL (0x4F) bit 5: VOUT_DROP_FAST_DROP_MASK
		"""
		return self.bits_read(0x4F, 1, 5)

	def write_vout_drop_fast_drop_mask(self, value):
		"""
		Write VOUT_DROP_CTRL (0x4F) bit 5: VOUT_DROP_FAST_DROP_MASK
		"""
		self.bits_write(value, 0x4F, 1, 5)

	def read_vout_delta(self):
		"""
		Read VOUT_DROP_CTRL (0x4F) bit 3:2: VOUT_DELTA
		Adjust threshold voltage
		"""
		return self.bits_read(0x4F, 2, 2)

	def write_vout_delta(self, value):
		"""
		Write VOUT_DROP_CTRL (0x4F) bit 3:2: VOUT_DELTA
		Adjust threshold voltage
		"""
		self.bits_write(value, 0x4F, 2, 2)

	def read_vout_delta_avg(self):
		"""
		Read VOUT_DROP_CTRL (0x4F) bit 1:0: VOUT_DELTA_AVG
		Adjust RC
		"""
		return self.bits_read(0x4F, 2, 0)

	def write_vout_delta_avg(self, value):
		"""
		Write VOUT_DROP_CTRL (0x4F) bit 1:0: VOUT_DELTA_AVG
		Adjust RC
		"""
		self.bits_write(value, 0x4F, 2, 0)


# ==================== Initialization ====================

	def initial(self):
		"""
		Init routine before efficiency test:
		1. Enable ADC
		2. Set VUSB_OVP / VEXT_OVP to max (25V)
		3. Enter Standby Mode
		4. Disable Watchdog
		5. Disable IIN_REG / VBAT_REG
		6. Disable VBAT_OVP / VOUT_OVP / IIN_OCP
		7. Set REG thresholds to maximum
		"""
		self.write_adc_en(1)
		self.write_vusb_sw_ctrl1(1)
		self.write_vext_sw_ctrl1(1)
		self.write_vusb_ovp(25)
		self.write_vext_ovp(25)
		self.write_standby_mode_set(1)
		self.write_wd_timeout_dis(1)
		self.write_iin_reg_dis(1)
		self.write_vbat_reg_dis(1)
		self.write_vbat_ovp_dis(1)
		self.write_vbat_ovp(5.115)
		self.write_vout_ovp_dis(1)
		self.write_iin_ocp_dis(1)
		self.write_iin_ocp(6375)
		self.write_iin_ucp_dis(1)
		self.write_iin_reg(6000)
		self.write_vbat_reg(5.115)
		self.write_ss_timeout(0)
		self.write_ntc_adc_dis(1)
		self.write_c1p2out_uvp(2)
		self.write_vusb_off_gate_ctrl(0)
# ==================== Fault Check ====================

	def read_fault_flag_registers(self):
		"""
		Read and decode INT_FAULT0~INT_FAULT6 (0x05~0x0B),
		plus late flag bits in 0x4B~0x4F.

		Each register byte is read exactly once before any bit is decoded,
		so multiple flags in the same register are not lost.

		Returns:
			raw_flags: {register_address: byte_value}
			asserted_flags: list of asserted flag descriptions
		"""
		flag_map = {
			0x05: {
				7: "IIN_OCP", 6: "IIN_UCP_FALL", 5: "VIN_OVP",
				4: "VB_OUT_OVP", 1: "VOUT_OVP", 0: "VBAT_OVP",
			},
			0x06: {
				7: "C1A_SHORT", 6: "C1B_SHORT", 5: "C2A_SHORT",
				4: "C2B_SHORT", 3: "C1A_OPEN", 2: "C1B_OPEN",
				1: "C2A_OPEN", 0: "C2B_OPEN",
			},
			0x07: {
				7: "PIN_DIAG_FAIL", 1: "PMID_ERRORHI", 0: "PMID_ERRORLO",
			},
			0x08: {
				7: "BST1A_SHORT", 6: "BST1B_SHORT", 5: "BST2_SHORT",
				4: "BST3A_SHORT", 3: "BST3B_SHORT", 2: "BST1A_OPEN",
				1: "BST1B_OPEN", 0: "BST2_OPEN",
			},
			0x09: {
				7: "BST3A_OPEN", 6: "BST3B_OPEN", 3: "EXT1_DRV_SHORT",
				2: "EXT1_FET_OPEN", 1: "EXT2_DRV_SHORT",
				0: "EXT2_FET_OPEN",
			},
			0x0A: {
				7: "C1A_SHORT_PH3", 6: "C1B_SHORT_PH3",
				5: "C2A_SHORT_PH3", 4: "C2B_SHORT_PH3", 3: "Q5_SHORT",
				2: "C1PA_C1PB_SHORT", 1: "Q3A_SHORT", 0: "Q3B_SHORT",
			},
			0x0B: {
				7: "CONV_OCP", 6: "VO12OUT_UVP", 5: "C1P2OUT_UVP",
				4: "C1P2OUT_OVP", 3: "NTC_FLT", 2: "TSHUT",
				1: "SS_FAIL", 0: "SS_TIMEOUT",
			},
			0x4E: {
				4: "QB_RCP",
			},
			0x4F: {
				6: "VOUT_DROP_FAST_DROP",
			},
		}

		raw_flags = {reg_addr: self.reg_read(reg_addr) for reg_addr in flag_map}
		asserted_flags = []
		for reg_addr, bit_map in flag_map.items():
			for bit, flag_name in bit_map.items():
				if raw_flags[reg_addr] & (1 << bit):
					asserted_flags.append(
						f"{flag_name}_FLAG (reg 0x{reg_addr:02X} bit{bit})"
					)
		return raw_flags, asserted_flags

	def read_all_fault_flags(self):
		"""
		Read all INT_FAULT0~INT_FAULT6 registers (0x05~0x0B).
		Raises RuntimeError with the exact flag name(s) if any fault flag is set.
		"""
		_raw_flags, errors = self.read_fault_flag_registers()

		if errors:
			raise RuntimeError(
				"Fault flag(s) detected:\n  " + "\n  ".join(errors)
			)

# ==================== Mask Control ====================

	def disable_all_masks(self):
		"""
		Disable all interrupts by setting all mask registers to 0xFF.
		Mask registers: MASK_DEVICE0~3 (0x0C~0x0F) + MASK_FAULT0~3 (0x10~0x13).
		"""
		mask_regs = range(0x0C, 0x14)  # 0x0C ~ 0x13
		for reg_addr in mask_regs:
			self.bits_write(0xFF, reg_addr, 8, 0)

# ==================== CP Startup ====================

	def cp_startup(self, qb="QB1", mode="4to1"):
		"""
		Start charge pump with specified QB and conversion ratio.

		Args:
			qb:  "QB1" = USB-IN path | "QB2" = WPC-IN path
			mode: "4to1","3to1","2to1","1to1","1to4","1to3","1to2","1to1_rev"
		"""
		# Map mode string to register value
		if mode == "4to1":
			mode_val = 0
		elif mode == "3to1":
			mode_val = 1
		elif mode == "2to1":
			mode_val = 2
		elif mode == "1to1":
			mode_val = 3
		elif mode == "1to4":
			mode_val = 4
		elif mode == "1to3":
			mode_val = 5
		elif mode == "1to2":
			mode_val = 6
		elif mode == "1to1_rev":
			mode_val = 7
		else:
			raise ValueError(f"Unknown mode='{mode}'.")

		is_reverse_mode = mode_val >= 4
		self.write_mode(mode_val)

		if is_reverse_mode:
			self.write_vo12out_uvp(3)

		if qb == "QB1":
			self.write_qb1_ctrl2(1)
		elif qb == "QB2":
			
			if self.read_qb2_ctrl1() == 1:
	
				raise ValueError("QB2 is in AUTO mode. Cannot manually control QB2.")
			self.write_qb2_ctrl2(1)
		else:
			raise ValueError(f"Unknown qb='{qb}'. Use 'QB1' or 'QB2'.")
		time.sleep(1)
		self.write_cp_en(1)
		time.sleep(1)
		self.write_cp_en(1)
		time.sleep(1)
		if self.read_cp_switching_stat() == 0:
			raise RuntimeError("CP startup failed: CP_SWITCHING_STAT did not assert.")
		if is_reverse_mode:
			if qb == "QB1":
				self.write_vusb_sw_ctrl1(0)
				self.write_vusb_sw_ctrl2(1)
			else:
				self.write_vext_sw_ctrl1(0)
				self.write_vext_sw_ctrl2(1)

		if self.read_cp_switching_stat() == 0:
			raise RuntimeError("CP startup failed: CP_SWITCHING_STAT did not assert when OVP FET CLOSE")

	def cp_shutdown(self):
		"""
		Shutdown charge pump (write 0 to CP_EN bit).
		"""
		self.write_cp_en(0)






